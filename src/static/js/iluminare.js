$(document).ready(function(){
    function bindclickpacientes(){
        $("#tabela-pacientes a").click(function(){
            var paciente = $(this).attr('id');
            var classe   = $(this).attr('class');
            var url = '';

            if (classe == 'checkin'){
                url = '/paciente/checkin/' + paciente;
            } else {
                url = '/paciente/consultar/' + paciente;
            }
            
            var motion = {'transitionIn':'elastic', 'transitionOut':'elastic'};
            $.get(url,function (data){$.fancybox(data, motion);});
        });
    }

    $("#q-paciente").keyup(function(key){
        var nome = $(this).val();
        $("#search-results").load('/paciente/search/' + encodeURIComponent(nome),
            bindclickpacientes);
    });
});

