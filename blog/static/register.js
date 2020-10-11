$(function () {
    var $sendmsg=$("#sendmsg");
    $sendmsg.click(function () {
        console.log('dddd');
        $.post('/sendmsg/',{})
    })
})