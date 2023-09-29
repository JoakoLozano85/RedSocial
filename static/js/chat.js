
$(document).ready(function(){
    $('#myMessage').keypress(function(e){
      if(e.keyCode==13)
      $('#send').click();
    });
});



const socket = io();

    //socket.emit('message', 'hello');

    socket.on('message', function (msg) {
        $('#messages').append('<li class="lista">' + msg + '</li>');
    })

    $('#send').on('click', function () {
        socket.send(($('#usuario')).val() +($('#sepa')).val() +  $('#myMessage').val());
        $('#myMessage').val('');
    });