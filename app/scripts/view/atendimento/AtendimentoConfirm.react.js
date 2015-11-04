var React = require('react');
var jquery = require('jquery');
var Rx = require('rx');
var MaterialUI = require('material-ui'),
  SelectField = MaterialUI.SelectField,
  RaisedButton = MaterialUI.RaisedButton;

var model = {};
var subscription1;
var subscription2;

var AtendimentoConfirm = React.createClass({
  getInitialState: function() {
    return {
      'tratamentos': [],
      'redirecionamento': null,
      'frequencia': null,
      'errorFrequencia': ''
    };
  },
  componentDidMount: function() {
    model.byIdAction.onNext(this.props.params.id);

    var atendimentos = model.byIdStore.flatMap(x => x.results);
    subscription1 = atendimentos.subscribe(this.setState.bind(this));

    subscription2 = Rx.Observable.combineLatest(
      model.tratamentos,
      atendimentos,
      function(t,a) {
        var tr = t.results;
        return {'tratamentos': tr.filter(z =>
            z.dia_semana === a.instancia_tratamento.tratamento.dia_semana
            && z.id != a.instancia_tratamento.tratamento.id)};
      }
    ).subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription1.dispose();
    subscription2.dispose();
  },
  _onChange: function(key, e) {
    this.setState({[key]: e.target.value});
  },
  _onTouchTap: function(e) {
    let error = this.state.redirecionamento !== null && this.state.frequencia === null;
    this.setState({errorFrequencia: error ? 'Selecione uma frequencia' : ''});

    model.update.onNext(this.state);
  },
  render: function () {
    let menuItems = [
       { payload: 'S', text: 'Semanal' },
       { payload: 'Q', text: 'Quinzenal' },
       { payload: 'M', text: 'Mensal' },
       { payload: 'O', text: 'Outro' },
    ];
    if (this.state.paciente) {
      return (
        <div>
          <h3>Senha {this.state.senha}{this.state.status}: {this.state.paciente.nome}</h3>
          <p>{this.state.prioridade ? 'É ' : 'Não é '} prioridade. Chegou às {this.state.hora_chegada} para o tratamento {this.state.instancia_tratamento.tratamento.descricao_basica}.</p>
          <SelectField
            fullWidth={true}
            floatingLabelText="Encaminhar para o tratamento"
            valueMember="id"
            displayMember="descricao_basica"
            value={this.state.redirecionamento}
            onChange={this._onChange.bind(this, 'redirecionamento')}
            menuItems={this.state.tratamentos} />
          <SelectField
            fullWidth={true}
            hintText="Frequencia"
            floatingLabelText="Frequencia"
            valueMember="payload"
            displayMember="text"
            errorText={this.state.errorFrequencia}
            value={this.state.frequencia}
            onChange={this._onChange.bind(this, 'frequencia')}
            menuItems={menuItems} />
          <RaisedButton
            label="Confirmar atendimento"
            primary={true}
            style={{'marginTop': '20px'}}
            onTouchTap={this._onTouchTap} />
        </div>
      )
    } else {
      return (
        <div>
          <h4>Aguarde! carregando dados...</h4>
        </div>
      )
    }
  }
});

function create(atendimentoModel, tratamentoModel) {
  if (!atendimentoModel.byIdAction)
    throw new Error('byIdAction is required');

  if (!atendimentoModel.byIdStore)
    throw new Error('byIdStore is required');

  if (!tratamentoModel.tratamentos)
    throw new Error('tratamentoModel.tratamentos is required');

  jquery.extend(model, atendimentoModel, tratamentoModel);
  return AtendimentoConfirm;
}

module.exports = create;
