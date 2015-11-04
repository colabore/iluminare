var jquery = require('jquery');
var React = require('react');
var Rx = require('rx');
var MaterialUI = require('material-ui'),
  RaisedButton = MaterialUI.RaisedButton,
  Tab = MaterialUI.Tab,
  Tabs = MaterialUI.Tabs,
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem;

var dia_semana = {
  "D": "Domingo",
  "S": "Segunda",
  "T": "Terça",
  "Q": "Quarta",
  "N": "Quinta",
  "X": "Sexta",
  "B": "Sábado"
}

var subscription1;
var subscription2;
var model = {};

var TratamentoDetails = React.createClass({
  getInitialState: function() {
    return {
      tratamento: {
        descricao_basica: 0,
        dia_semana: "B",
        id: 0},
      instanciatratamento: [],
      hasAtendimento: false
    };
  },
  componentDidMount: function() {
    model.instanciatratamento.getByTratamentoId.onNext(this.props.params.id);

    var tratamentoStore = model.tratamento.tratamentos
      .flatMap(x => x.results
        .filter(y => y.id === parseInt(this.props.params.id, 10))
      );

    subscription1 = Rx.Observable.combineLatest(
      model.instanciatratamento.byTratamentoId,
      tratamentoStore,
      function (x,y) {
        return jquery.extend({}, {instanciatratamento: x.results}, {tratamento: y});
      }
    ).subscribe(this.setState.bind(this));

    subscription2 = model.instanciatratamento.byTratamentoId
      .subscribe(function(x) {
        if (x.results.length == 0)
          return;

        var last = new Date(Date.parse(x.results[0].data));
        var today = new Date(Date.now());

        var hasAtendimento = last.getFullYear() === today.getFullYear()
          && last.getMonth() === today.getMonth()
          && last.getDay() === today.getDay();

        this.setState({
          hasAtendimento: hasAtendimento
        });
      }.bind(this));
  },
  componentWillUnmount: function() {
    subscription1.dispose();
    subscription2.dispose();
  },
  _items: function(data){
    return (
      <ListItem
        id={data.id}
        key={data.id}>
      {(new Date(Date.parse(data.data))).toLocaleDateString("latn")}
      </ListItem>
    );
  },
  _abrirTrabalhos: function(e) {
    model.instanciatratamento.create.onNext(e.currentTarget.id);
  },
  render: function() {
    var atendimento = this.state.hasAtendimento ?
      <p>Os atendimentos para esse tratamento podem ser iniciados</p> :
      <span>
        <p>Os atendimentos para esse tratamento ainda não iniciaram hoje.</p>
        <RaisedButton
          label="Abrir trabalhos de hoje"
          onTouchTap={this._abrirTrabalhos} />
      </span>

    var items = this.state.instanciatratamento.map(this._items);
    return (
      <div>
        <h1>{this.state.tratamento.descricao_basica} / {dia_semana[this.state.tratamento.dia_semana]}</h1>
        <Tabs>
          <Tab label="Hoje" >
            {atendimento}
          </Tab>
          <Tab label="Últimos atendimentos" >
            <List>
              {items}
            </List>
          </Tab>
        </Tabs>
      </div>
    )
  }
});

function create(options) {
  if (!options.tratamento)
    throw new Error('tratamento is required');

  model = options;
  return TratamentoDetails;
}

module.exports = create;
