$(document).ready(function(){
    $(".obos-choose").click(function(){
        var obos_selected = event.target.id;
        var url = "{% url 'market:market' %}";
        $.ajax({
            type:'POST',
            url:"{%url 'market:market'%}",
            data:{'obos_selected':obos_selected},
            success:function(e){
                console.log(e);
            },
        })
    })
})