function getRecommendations() {
    var location = document.getElementById("location").value;
    var rating = document.getElementById("rating").value;
    var tags = $('#tags').val();

    $.ajax({
        type: "POST",
        url: "/recommendations",
        data: {
            location: location,
            rating: rating,
            tags: tags
        },
        success: function(response) {
            $('#recommendations').html(response);
        }
    });
}
