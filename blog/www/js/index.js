/**
 * Created by Administrator on 11/3/2019.
 */
$(function () {
    $("#loginUserNc,#userOprBox").mouseover(function () {
        $("#userOprBox").removeClass('hide')
    })
    $("#loginUserNc,#userOprBox").mouseout(function () {
        $("#userOprBox").addClass('hide')
    })
    $('.logout').click(function () {
        $(this).attr("href", "/login_out/")
    })
});

function login() {
    $("#go_grey, #login_window").removeClass('hide');
};
function close_login() {
    $("#go_grey, #login_window").addClass('hide');
};
function BandGetCode(ths) {
    $('.err-msg,.err-sum').empty();
    var email = $('#email').val();
    if (email.trim().length == 0) {
        $('.err-sum').text('请输入邮箱');
        return;
    }
    ;
    if ($(this).hasClass('sending')) {
        // 遇到return下面不再继续执行
        return;
    }
    var time = 60;
    $.ajax({
        url: "/send_msg/",
        type: "POST",
        data: {email: email},
        dataType: "json",
        success: function (arg) {
            if (!arg.status) {

                console.log(arg.summary)
                $('.err-sum').text(arg.summary);
            } else {
                $(ths).addClass('sending');
                var interval = setInterval(function () {
                    time -= 1;
                    $(ths).text('已发送(' + time + ')');
                    if (time <= 0) {
                        $(ths).removeClass('sending');
                        $(ths).text('获取验证码');
                        clearInterval(interval);
                    }
                }, 1000)
            }
        }
    })
}

function BandRegister() {
    $('.err-msg,.err-sum').empty();
    var all_data = $('#all_data').serialize();
    $.ajax({
        url: "/register/",
        type: "POST",
        data: all_data,
        dataType: "json",
        success: function (arg) {
            if (arg.status) {
                window.location.reload();
            } else {
                var i = 0;
                $.each(arg.message, function (k, v) {
                    $('.' + k + '')[0].innerText = arg.message[k][0]['message'];
                })
            }
        }
    })
}

function SubmitLogin() {
    $('.err-msg').empty();
    var all_data = $('#login_all_data').serialize();
    $.ajax({
        url: "/login/",
        type: "POST",
        data: all_data,
        dataType: "json",
        success: function (arg) {
            console.log(arg.message);
            if (arg.status) {
                window.location.reload();
            } else {
                $.each(arg.message, function (key, val) {
                    var msg = arg.message[key][0]['message'];
                    console.log(msg);
                    var tag = document.createElement('span');
                    tag.innerText = msg;
                    tag.className = 'err-msg';
                    $("input[name='" + key + "']").before(tag);
                })

            }
        }
    })
}
function ChangeCode(ths) {
    ths.src += '?';

}