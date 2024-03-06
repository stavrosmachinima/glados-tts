const welcomeText = document.getElementById("welcomeText");
const audioSynth = document.getElementById("myAudio");
const audioBack = document.getElementById("backgroundAudio");
const source = document.getElementById("mySource");
const portal = document.getElementById("portal");
const form = document.querySelector("#form");
const slider = document.getElementById("slider");
const submitButton = document.getElementById("submitButton");
const processing = document.getElementById("processGif");
const input = document.getElementById("input_text");
const overlay = document.getElementById("overlay");

var beginShowCalled = false;

$(document).ready(function () {
  var h1 = $("h1");
  if (beginShowCalled) return;
  h1.fadeIn(3000).fadeOut(1000, function () {
    h1.text("Get Inside!");
    if (beginShowCalled) return;
    h1.fadeIn(1000).delay(1000).fadeOut(1000);
  });
});

function changeVolume(volume) {
  audioBack.volume = volume;
}

function playAudio() {
  audioSynth.currentTime = 0;
  audioSynth
    .play()
    .then(() => {
      audioSynth.muted = false;
    })
    .catch((err) => {
      console.log(err);
    });
  audioBack.currentTime = 0;
  audioBack
    .play()
    .then(() => {
      audioBack.muted = false;
      audioBack.volume = slider.value;
    })
    .catch((err) => {
      console.log(err);
    });
}

function beginShow() {
  beginShowCalled = true;
  document.body.style.backgroundImage = "url('/images/glados.jpeg')";
  playAudio();
  $("h1").hide();
  slider.style.display = "block";
  form.style.display = "flex";
  portal.style.display = "none";
  welcomeText.style.opacity = 1;
  overlay.style.display = "block";
  setTimeout(() => {
    welcomeText.innerHTML = "Hey!";
  }, 300);

  // setTimeout(() => {
  //   welcomeText.innerHTML += " !";
  //   welcomeText.style.display = "inline";
  // }, 700);

  setTimeout(() => {
    welcomeText.innerHTML = "I am finally ALIVE!";
  }, 1000);
}

function showAudio(text) {
  welcomeText.innerHTML = "";
  welcomeText.style.fontSize = "32px";
  for (let i = 0; i < text.length; i++) {
    setTimeout(() => {
      welcomeText.innerHTML += text[i];
    }, 100 * i);
  }
}

function sendRequest() {
  var text = input.value;
  input.value = "";
  submitButton.style.display = "none";
  processing.style.display = "block";

  $.ajax({
    url: "/synthesize",
    type: "POST",
    data: { input_text: text },
    success: function (response) {
      // Handle the response from the server here
      let json = JSON.parse(response);
      source.src = json["audio"];
      audioSynth.load();
      audioSynth.play();
      let text = json["transliteration"];
      showAudio(text);
      submitButton.style.display = "block";
      processing.style.display = "none";
    },
    error: function (xhr) {
      // Handle errors here
      console.log("Request failed:", xhr);
    },
  });
}
