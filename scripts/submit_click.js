let dict; // global var type shit

document.getElementById("form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent page reload

    let url = document.getElementById("url").value;
    const songCard = document.getElementById("song-card");
    const errorMessage = document.getElementById("error");
    const noSongError = document.getElementById("no-song-error")
    const albumCover = document.getElementById("cover");
    const loading = document.getElementById("loading");

    songCard.classList.remove("show");
    errorMessage.classList.remove("show");
    noSongError.classList.remove("show");
    loading.classList.add("show");
    albumCover.src = "media/default-cover.jpg"


    try {
        getData(url).then(() => {
            console.log(dict)

            // Fades out loading thing
            loading.style.animation = "fadeOut 0.25s forwards"
            setTimeout(function() {
                loading.classList.remove("show");

                // Stores output data to dict variable
                if (dict.success === true) { // If a song was found
                    document.getElementById("spotify").href = dict.spotify;
                    document.getElementById("yt-music").href = dict.youtube;
                    document.getElementById("apple-music").href = dict.apple;
                    document.getElementById("title").textContent = dict.title;
                    document.getElementById("artist").textContent = dict.artist;

                    if (dict.cover === true) {
                        albumCover.src = "media/cover.jpg?v=" + new Date().getTime();
                        songCard.style.backgroundColor = dict.color;
                        songCard.style.color = dict.text_color;
                    }


                    songCard.classList.add("show");
                    songCard.style.animation = "fadeIn 0.5s forwards"
                } else { // If no song was found
                    if (dict.error === "NO_SONG_FOUND") {
                        noSongError.classList.add("show");
                        noSongError.style.animation = "fadeIn 0.5s forwards"
                    } else {
                        errorMessage.textContent = dict.error;
                        errorMessage.classList.add("show");
                        errorMessage.style.animation = "fadeIn 0.5s forwards"
                    }
                }
            }, 250);
        });
    } catch (error) {
        errorMessage.textContent = `JS Error: ${error}`;
        errorMessage.classList.add("show");
        console.error("JS Error:", error);
    }
});

async function getData(text) {
    const response = await fetch('http://127.0.0.1:5000/process', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "url": text
        })
    });
    dict = await response.json();  // Assign data
}

function handleSubmit(event) {
    event.preventDefault(); // Prevent the form from submitting immediately

    document.getElementById("submit").classList.add("animate"); // Trigger your animation
    document.getElementById("form").style.marginTop = "5rem";

    setTimeout(() => {
        try {
            let form = document.getElementById("form");
            if (form && form.tagName === "FORM") {
                form.submit();
            } else {
                console.error("Element with ID 'form' is not a form.");
            }
        } catch (error) {
            console.error(error);
        }
    }, 500);
}