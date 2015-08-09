var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  SelectField = MaterialUI.SelectField,
  RaisedButton = MaterialUI.RaisedButton;

var subscription1;

var AtendimentoConfirm = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return { muiTheme: ThemeManager.getCurrentTheme() }
  },
  getInitialState: function() {
    return {}
  },
  componentDidMount: function() {
    var source = this.props.atendimentoStore.flatMap(x => x.results);
    subscription1 = source.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription1.dispose();
  },
  render: function () {
    let menuItems = [
       { payload: '1', text: 'Never' },
       { payload: '2', text: 'Every Night' },
       { payload: '3', text: 'Weeknights' },
       { payload: '4', text: 'Weekends' },
       { payload: '5', text: 'Weekly' },
    ];
    if (this.state.paciente) {
      return (
        <div>
          <h3>Senha {this.state.senha}{this.state.status}: {this.state.paciente.nome}</h3>
          <p>{this.state.prioridade ? 'É ' : 'Não é '} prioridade. Chegou às {this.state.hora_chegada} para o tratamento {this.state.instancia_tratamento.tratamento.descricao_basica}.</p>
          <SelectField
            fullWidth={true}
            floatingLabelText="Encaminhar para o tratamento"
            valueMember="payload"
            displayMember="text"
            menuItems={menuItems} />
          <SelectField
            fullWidth={true}
            hintText="Frequencia"
            floatingLabelText="Frequencia"
            valueMember="payload"
            displayMember="text"
            menuItems={menuItems} />
          <RaisedButton label="Confirmar atendimento" primary={true} />
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

module.exports = AtendimentoConfirm;
