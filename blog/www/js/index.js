/**
 * Created by Administrator on 11/3/2019.
 */

$(document).ready(
    function ready_page(){
		$.ajax({
			url: "/api/v1/user-centre/user-info",
            type: "get",
			success: function (rep) {
				logged(rep);
			},
			error: function () {
                login_required()
            }
		});
		function logged(rep) {
		    var message = rep["message"];
		    if (!message){
		        login_required();
                return
            }
		    if (message["username"]){
                $(".sign").addClass("hide");
                $(".logged").removeClass("hide");
                $(".user-info").text(message["username"]);
            }else{
		        login_required();
            }
        }
        function login_required() {
            $(".sign").removeClass("hide");
		    $(".logged").addClass("hide");
        }

	});
$(function () {
    $(".user-info").mouseover(function () {
        $("#userOprBox").removeClass('hide')
    });
    $("#userOprBox").mouseleave(function () {
        $("#userOprBox").addClass('hide')
    });
    $('.logout').click(function () {
        $(this).attr("href", "/api/v1/user-centre/session/")
    })
});

function sign_in() {
    $("#sign_in, #login_window").removeClass('hide');
    $('.err-msg').empty();
    $('.check-img').attr("src", "/api/v1/user-centre/login_code");
}

function sign_up() {
    $("#sign_up, #register_window").removeClass('hide');
    $('.err-msg').empty();
}

function close_login() {
    $("#sign_in, #login_window").addClass('hide');
}

function close_register() {
    $("#sign_up, #register_window").addClass('hide');
}
function BandGetCode(ths) {
    $('.err-msg,.err-sum').empty();
    var email = $('#email').val();
    if (email.trim().length == 0) {
        $('.err-sum').text('please input your email address');
        return;
    }

    if ($(ths).hasClass('sending')) {
        // 遇到return下面不再继续执行
        return;
    }
    $(ths).addClass('sending');
    $(ths).addClass('disable');
    $(ths).text('sent');
    var time = 60;
    $.ajax({
        url: "/api/v1/user-centre/email/",
        type: "GET",
        data: {email: email},
        dataType: "json",
        success: function (arg) {
            if (arg.code !== 200) {
                $('.err-sum').text(arg.error);
            } else {
                var interval = setInterval(function () {
                    time -= 1;
                    $(ths).text('sent(' + time + ')');
                    if (time <= 0) {
                        $(ths).removeClass('sending');
                        $(ths).removeClass('disable');
                        $(ths).text('Get verify code');
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
        url: "/api/v1/user-centre/user/",
        type: "POST",
        data: all_data,
        dataType: "json",
        success: function (arg) {
            if (arg.code === 201) {
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
        url: "/api/v1/user-centre/session/",
        type: "POST",
        data: all_data,
        dataType: "json",
        success: function (arg) {
            if (arg.code === 200) {
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