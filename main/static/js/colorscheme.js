function getCookie(name) {
  var matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function drawcolor(){
    cook = getCookie('color');
    // console.log(cook)
    if (cook === undefined){
        document.cookie = "color=red; path=/";
        cook = 'red';
    }
    if (cook === 'red'){
        $('#logo_img').attr('src', '../static/img/logo_red.svg')
        $('#style-color').append('.layout-color{background: var(--color-red);}'+
                            '.layout-color-inv{background: var(--color-blue);}');
    }
    else{
        $('#logo_img').attr('src', '../static/img/logo_blue.svg')
        $('#style-color').append('.layout-color{background: var(--color-blue);}'+
                            '.layout-color-inv{background: var(--color-red);}');
    }
    // console.log(document.cookie);
}

function changecolor(){
    cook = getCookie('color');
    if (cook === 'red'){
        $('#logo_img').attr('src', '../static/img/logo_blue.svg')
        document.cookie = "color=blue; path=/";
        $('#style-color').html(':root {--color-red: #e44332ff;--color-blue: #1B92C6;} .layout-color{background: var(--color-blue);}'+
                        '.layout-color-inv{background: var(--color-red);}');
    }
    else{
        $('#logo_img').attr('src', '../static/img/logo_red.svg')
        document.cookie = "color=red; path=/";
        $('#style-color').html(':root {--color-red: #e44332ff;--color-blue: #1B92C6;} .layout-color{background: var(--color-red);}'+
                        '.layout-color-inv{background: var(--color-blue);}');
    }
}