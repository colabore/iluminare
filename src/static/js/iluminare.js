$(document).ready(function(){
    function bindclickpacientes(){
        $("#tabela-pacientes a").click(function(){
            var paciente = $(this).attr('id');
            $.get('/paciente/consultar/' + paciente,
                function (data){
                    $.fancybox(data, {'transitionIn':'elastic', 'transitionOut':'elastic'});
                });
        });
    }

    $("#q-paciente").keyup(function(key){
        var nome = $(this).val();
        $("#search-results").load('/paciente/search/' + encodeURIComponent(nome),
            bindclickpacientes);
    });
});

