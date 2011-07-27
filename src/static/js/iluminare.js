$(document).ready(function(){
    function bindclickpacientes(){
        $("#iluminare #tabela-pacientes a").click(function(){
            var paciente_tratamento = $(this).attr('id');
            alert(paciente_tratamento);
        });
    }

    $("#q-paciente").keyup(function(key){
        var nome = $(this).val();
        $("#search-results").load('/paciente/search/' + encodeURIComponent(nome),
            bindclickpacientes);
    });
});

