var urls = require('../utils/ApiUrls');
var jquery = require('jquery');
var Rx = require('rx');

function create2(action) {
  return action.subscribe(
    function (id) {
      var date = new Date(Date.now());
      var dateString = date.getFullYear()
        + '-' + date.getMonth()
        + '-' + date.getDay();

      let params = {
        'coletivo': false,
      };
      jquery.ajax({
         url: '//localhost:8000/api/instanciatratamento/',
         type: 'POST',
         contentType: "application/json",
         dataType: 'text',
         data: JSON.stringify({
           "coletivo": false,
           "data": dateString,
           "tratamento": {id: 1}
         }),
         success: function(response) {
           console.log(response);
         },
         error: function(response) {
           console.log(response);
         }
      });
    }
  );
};

function create(options) {
  var model = {
    byDateStore: new Rx.ReplaySubject(),
  };
  jquery.extend(model, options);

  create2(model.create);

  return model;
}

module.exports = create;
