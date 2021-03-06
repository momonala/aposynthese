const express = require("express");
const app = express();
const fs = require("fs");
const path = require("path");
const spawn = require("await-spawn");
const bodyParser = require("body-parser");

app.use(bodyParser.urlencoded({ extended: true }));

// serve static resources
app.use("/assets", express.static(__dirname + "/assets"));

// homepage endpoint. __dirname will resolve to project folder.
app.get("/",function(req,res) {
    res.sendFile(path.join(__dirname+"/templates/homepage.html"));
});

// temp endpoint to handle data for a post request for an input youtube link
app.post("/handle_data", function(req, res){
    console.log("Incoming request: YT UUID: "+req.body);
    response = {yt_link : req.body.yt_link};

    // spawn the decomposition python pipeline
    const { spawn } = require("child_process");
    const pythonProcess = spawn("python3", ["audio_to_piano.py",  "--youtube", req.body.yt_link]);

    // event callback to see python logs
    pythonProcess.stdout.on("data", function(data) {
        python_logs = data.toString();
        console.log(python_logs);
    });

    // wait for python process to finish, redirect to streaming endpoint or error handling.
    pythonProcess.on("close", (code) => {
        console.log(`child process exited with code ${code}`);
        if (code > 0) {
            return res.status(500).send({message: python_logs});
        }

        console.log("Decomposing Sucessful! Redirecting to stream video.")
        var fullUrl = req.protocol + "://" + req.get("host");
        var youtube_uuid = req.body.yt_link.split("=")[1];
        res.redirect(fullUrl+"/decomposed/?yt_id="+youtube_uuid);
    });
});


// endpoint to stream final video output
// credit where due: https://github.com/daspinola/video-stream-sample/blob/master/server.js
app.get("/decomposed", (req, res) => {
    var yt_id = req.query.yt_id;
    var output_vid_path = "output/"+yt_id+".mp4";
    // extract video file metadata info for chunking
    const stat = fs.statSync(output_vid_path);
    const fileSize = stat.size;
    const range = req.headers.range;

    if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize-1;

        // create stream buffer
        const chunksize = (end-start)+1;
        const file = fs.createReadStream(output_vid_path, {start, end});
        const head = {
          "Content-Range": `bytes ${start}-${end}/${fileSize}`,
          "Accept-Ranges": "bytes",
          "Content-Length": chunksize,
          "Content-Type": "video/mp4",
        }

        // return http 206 partial content header
        res.writeHead(206, head);
        file.pipe(res);
    }
    else {
        const head = {
          "Content-Length": fileSize,
          "Content-Type": "video/mp4",
        }
        res.writeHead(200, head);
        fs.createReadStream(output_vid_path).pipe(res);
    }
});


// launch the server
var server = app.listen(80, function(){
    var host = server.address().address;
    var port = server.address().port;
    server.timeout = 0;
    console.log("Application listening at http://%s:%s", host, port);
});
