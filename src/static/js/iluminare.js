$(document).ready(function(){
    function bindclickpacientes(){
        $("#tabela-pacientes a").click(function(){
            var paciente = $(this).attr('id');
            var classe   = $(this).attr('class');
            var url = '';

            if (classe == 'checkin'){
                url = '/atendimento/checkin/' + paciente;
            } else {
                url = '/paciente/consultar/' + paciente;
            }
            
            var motion = {'transitionIn':'elastic', 'transitionOut':'elastic'};
            $.get(url,function (data){$.fancybox(data, motion);bindfancybox(paciente);});
        });
    }
    function bindfancybox(paciente){
        $("#checkin_submit").click(function(){
            $.post('/atendimento/checkin/'+paciente, 
            $("#form_paciente_checkin").serialize(),
            function(data){
                $("#paciente_checkin").html(data);
                bindfancybox(paciente);
            });
        });

        $("#cadastro_checkin_rapido").click(function(){
            $.post('/paciente/cadastro-rapido/', 
            $("#form-cadastro-paciente").serialize(),
            function(data){
                $("#div-cadastro-paciente").html(data);
                bindfancybox(paciente);
            });
        });
            
    }
    function bindfancybox2(atendimento){
        $("#atualiza_paciente_confirma_submit").click(function(){
            $.post('/atendimento/atualizar-paciente-confirmacao/'+atendimento,
            $("#form_atualiza_paciente_confirma").serialize(),
            function(data){
                $("#atualiza_paciente_confirma").html(data);
                bindfancybox2(atendimento);
            });
        });

    }

    $("#q-paciente").keyup(function(key){
        var nome = $(this).val();
        if (key.keyCode == '13'){
            $("#search-results").load('/paciente/search/' + encodeURIComponent(nome),
                bindclickpacientes);
        }
    });
    $("#form-search").submit(function(){
        return false;
    })
    


    $("#tabela-fechamento a").click(function(){
        var atendimento = $(this).attr('id');
        var classe      = $(this).attr('class');
        var url = '/atendimento/atualizar-paciente-confirmacao/' + atendimento;
        var motion = {'transitionIn':'elastic', 'transitionOut':'elastic'};
        $.get(url,function (data){$.fancybox(data, motion);bindfancybox2(atendimento);});
    });

    $("#cadastro_rapido").click(function(){
        var motion = {'transitionIn':'elastic', 'transitionOut':'elastic'};
        $.get('/paciente/cadastro-rapido/',function (data){
            $.fancybox(data, motion);
            bindfancybox($(this).attr('id'));
            $('#id_nome').val($('#q-paciente').val());
        });
    });
});

