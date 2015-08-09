
let server = 'http://localhost:8000';
let atendimentoApi = '/api/atendimento/.json'
let instanciatratamentoApi = "/api/instanciatratamento/.json";
let pacienteApi = "/api/paciente/.json";

var ApiUrls = {
  atendimento: function(params) {
    return server + atendimentoApi + toString(params);
  },
  instanciatratamento: function(params) {
    return server + instanciatratamentoApi + toString(params);
  },
  paciente: function(params) {
    return server + pacienteApi + toString(params);
  }
};

function toString(params) {
  var urlParams = "?";
  for (var key in params) {
    urlParams += key + "=" + params[key] + "&";
  }
  return urlParams;
}

module.exports = ApiUrls;
