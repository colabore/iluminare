var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  Tabs = MaterialUI.Tabs,
  Tab = MaterialUI.Tab,
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem,
  TextField = MaterialUI.TextField;

var subscription;

var PacienteDetails = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return {
      muiTheme: ThemeManager.getCurrentTheme()
    };
  },
  getInitialState: function() {
    return {
      'nome': 'Nome do paciente'
    }
  },
  componentDidMount: function() {
    subscription = this.props.infoStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  render: function() {
    return (
      <div>
        <h2 className="paper-font-display2">Paciente</h2>
        <Tabs>
          <Tab label="Informações">
            <List>
              <ListItem>Nome: {this.state.nome}</ListItem>
            </List>
          </Tab>
          <Tab label="Tratamentos">
            <p>Informação não disponível</p>
          </Tab>
          <Tab label="Atendimentos">
            <p>Informação não disponível</p>
          </Tab>
        </Tabs>
      </div>
    )
  }
});

module.exports = PacienteDetails;
