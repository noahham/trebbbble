function handleSubmit(event) {
    event.preventDefault(); // Prevent the form from submitting immediately

    document.getElementById("submit").classList.add("animate"); // Trigger your animation
    document.getElementById("form").style.marginTop = "5rem";

    setTimeout(() => {event.target.submit();}, 500);
}

document.getElementById("form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent page reload

    const url = document.getElementById("url").value;
    const songCard = document.getElementById("song-card");
    const errorMessage = document.getElementById("error");

    songCard.classList.remove("show");
    errorMessage.classList.remove("show");

    try {
        const response = await fetch('/process', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById("spotify").href = data.spotify;
            document.getElementById("yt-music").href = data.youtube;
            document.getElementById("apple-music").href = data.apple;
            document.getElementById("title").textContent = data.title;
            document.getElementById("artist").textContent = data.artist;

            songCard.classList.add("show");
        } else {
            errorMessage.textContent = `Error: ${data.error}`;
            errorMessage.classList.add("show");
        }
    } catch (error) {
        errorMessage.textContent = "Network error. Please try again.";
        errorMessage.classList.add("show");
        console.error("Error:", error);
    }
});
