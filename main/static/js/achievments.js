function makeAchievementToast(achievmentImage, achievmentText, color, duration) {
    color = color == undefined ? "red" : color;
    const toastContent = '<img id="logo_img" src="' + achievmentImage + '" style="max-width: 2rem;"><span style="margin-left: 3rem;">' + "Achievment unlocked:<br>" + achievmentText + '</span> <button onclick="' + "javascript:window.location.href='/settings'" + '" class="btn-flat toast-actоion white red-text">Check it out!</button>';
    Materialize.toast(toastContent, duration == undefined ? 10000 : duration, "red");
}