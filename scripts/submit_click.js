function handleSubmit(event) {
    event.preventDefault(); // Prevent the form from submitting immediately

    document.getElementById("submit").classList.add("animate"); // Trigger your animation
    document.getElementById("form").style.marginTop = "5rem";

    setTimeout(() => {event.target.submit();}, 500);
}