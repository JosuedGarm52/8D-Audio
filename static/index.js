$("#convert").click(function(){
    $("#error").html("");
    const link = $(".input").val();
    if(!link){
        $("#error").html("field can't be empty");
        $(".input").select();
        return;
    }
    var regex = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*/;
    var match = link.match(regex);
    if(match == null){
        $("#error").html("enter a valid youtube link");
        return;
    }

    // 🔹 mostrar spinner en el botón
    $("#convert").addClass("spinner").prop("disabled", true);

    $.post("/convert", { url: link })
        .done(function(response){
            const errorMatch = response.match(/\{.*"error":.*\}/);
            if(errorMatch){
                const data = JSON.parse(errorMatch[0]);
                let msg = data.error;
                if(msg.length > 50) msg = msg.slice(0, 50) + "...";
                showErrorModal(msg);
                console.error("Error completo del servidor:", data.error);
                return;
            }

            $("#after_convert").css("display","block");
            $("#before_convert").removeClass("animated fadeIn");
            $("#after_convert").addClass("animated fadeIn");
            $("#before_convert").css("display","none");
            $("#max").css("display", "none");
            $(".input").css("display","none");
            $(".input").val("");
            $("#convert").css("display","none");
            $("#spinner").css("display","inherit");
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            showErrorModal("Error inesperado: " + textStatus);
            console.error("Error de red:", jqXHR.responseText || errorThrown);
        })
        .always(function(){
            // 🔹 quitar spinner al terminar
            $("#convert").removeClass("spinner").prop("disabled", false);
        });
});


$("#again").click(function(){
    document.getElementById("playa").load()
    $(".input").css("display","block");
    $("#convert").css("display","block");
    $("#before_convert").css("display","block");
    $("#before_convert").addClass("animated fadeIn");
    $("#after_convert").css("display","none");
    $("#after_convert").removeClass("animated fadeIn");
    $("#spinner").css("display","none");
});

$("#fork").click(function(){
    window.location.href = "https://github.com/maxgillham/8D-Audio";
})

setTimeout(function(){
    $("#loading").addClass("animated fadeOut");
    setTimeout(function(){
        $("#loading").removeClass("animated fadeOut");
        $("#loading").css("display","none");
    },800);
},3000);

function showSuccessModal() {
    $("#success-modal").addClass("show");
    // Ocultar después de 3 segundos
    setTimeout(function(){
        $("#success-modal").removeClass("show");
    }, 3000);
}

// use this when its done converting not setTimeout :)
function done() {
    $("#after_convert").css("display","block");
    $("#before_convert").removeClass("animated fadeIn");
    $("#after_convert").addClass("animated fadeIn");
    $("#before_convert").css("display","none");

    // Mostrar palomita de éxito
    showSuccessModal();
}

function showErrorModal(message) {
    $("#error-message").text(message);
    $("#error-modal").css("display","flex");
}

// Cerrar modal con botón
$("#close-error").click(function() {
    $("#error-modal").fadeOut();
});

// Cerrar modal con la X
$(".close-btn").click(function() {
    $("#error-modal").fadeOut();
});

// Cerrar modal al hacer clic fuera del contenido
$(window).click(function(event) {
    if ($(event.target).is("#error-modal")) {
        $("#error-modal").fadeOut();
    }
});

// Botón de ejemplo
$("#sample").click(function() {
    const sampleLink = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
    $(".input").val(sampleLink);
    $("#convert").click(); // activa la conversión automáticamente
});
