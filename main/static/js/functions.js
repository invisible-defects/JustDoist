function makeAchievementToast(achievementImage, achievementText, color, duration) {
    color = color == undefined ? "red" : color;
    const toastContent = '<img id="logo_img" src="' + achievementImage + '" style="max-width: 2rem;"><span style="margin-left: 3rem;">' + "Achievment unlocked:<br>" + achievementText + '</span> <button onclick="' + "javascript:window.location.href='/settings'" + '" class="btn-flat toast-actоion white red-text">Check it out!</button>';
    Materialize.toast(toastContent, duration == undefined ? 10000 : duration, "red");
}

function sendcolor(){
    hex = $('input[type="radio"]:checked').val();
        $.ajax({
        url: '/color',
        data: {hex: hex}, // TODO: add step handling
        type: "GET",
        async: true,
        error: function(jqXHR, exception) {alert(jqXHR);},
        success: function(data){$('#status').html('done');}
    });
}

function changecolor(color){
    $('#status').html('');
    $('#style-color').html(':root {--color-layout: var(--color-'+color+')');
    data = {"red": "#C32127", "blue": "#235D77", "green": "#367439"};
    $('#fill_body').attr("fill", data[color]);
}
function init_color(color){
    $('#content').prepend('<style id="style-color">:root {--color-layout: ' + color + ';}</style>');
    data = {"#e44332ff": "#C32127", "#1B92C6": "#235D77", "#48d34e": "#367439"};
    $('#fill_body').attr("fill", data[color]);
}