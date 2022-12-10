let video = document.getElementById("cam_input");
var canvas = document.getElementById("canvas");
var context = canvas.getContext("2d");

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({
      video: true,
    })
    .then(function (stream) {
      video.srcObject = stream;
      video.play();
    })
    .catch(function (err0r) {});
}

const FPS = 30;

function openCvReady() {
  function processVideo() {
    let begin = Date.now();
    width = 1280;
    height = 720;
    context.drawImage(video, 0, 0, width, height);
    var data = canvas.toDataURL("image/jpeg", 0.5);
    let fd = new FormData();
    fd.append("b64", data);
    fetch("/prediction", {
      method: "POST",
      body: fd,
    })
      .then((response) => response.json())
      .then((data) => console.log(data));
    // console.log("send data");
    context.clearRect(0, 0, width, height);

    // schedule next one.
    let delay = 1000 / FPS - (Date.now() - begin);
    setTimeout(processVideo, delay);
  }
  // schedule first one.
  setTimeout(processVideo, 0);
}
openCvReady();
