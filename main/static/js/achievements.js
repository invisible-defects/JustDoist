function makeAchievementToast(achievementImage, achievementText, color, duration) {
    color = color == undefined ? "red" : color;
    const toastContent = '<img id="logo_img" src="' + achievementImage + '" style="max-width: 2rem;"><span style="margin-left: 3rem;">' + "Achievment unlocked:<br>" + achievementText + '</span> <button onclick="' + "javascript:window.location.href='/settings'" + '" class="btn-flat toast-actоion white red-text">Check it out!</button>';
    Materialize.toast(toastContent, duration == undefined ? 10000 : duration, "red");
}