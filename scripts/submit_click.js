let dict; // global var type shit

document.getElementById("form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent page reload

    const url = document.getElementById("url").value;
    const songCard = document.getElementById("song-card");
    const errorMessage = document.getElementById("error");

    songCard.classList.remove("show");
    errorMessage.classList.remove("show");

    try {
        getData(url).then(() => {
            console.log(dict)
            // Stores output data to dict variable
            if (dict.success === true) { // If a song was found
                document.getElementById("spotify").href = dict.spotify;
                document.getElementById("yt-music").href = dict.youtube;
                document.getElementById("apple-music").href = dict.apple;
                document.getElementById("title").textContent = dict.title;
                document.getElementById("artist").textContent = dict.artist;

                songCard.classList.add("show");
            } else { // If no song was found
                errorMessage.textContent = `Error: ${dict.error}`;
                errorMessage.classList.add("show");
            }
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

    setTimeout(() => {(document.getElementById('form')).submit()}, 500);
}