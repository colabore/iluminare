
var React = require('react');
var MaterialUI = require('material-ui'),
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

var subscription;

var TratamentoList = React.createClass({
  getInitialState: function() {
   return {'results': []};
  },
  componentDidMount: function() {
    subscription = this.props.tratamentos.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  _onTouchTap: function(e) {
    document.location = document.location.origin + '/#/tratamento/details/' + e.currentTarget.id;
  },
  getMessageListItem: function(data) {
    return (
      <ListItem
        id={data.id}
        key={data.id}
        
        onTouchTap={this._onTouchTap}>
        {data.descricao_basica} / {dia_semana[data.dia_semana]}
      </ListItem>
    );
  },
  render: function() {
    var listItems = this.state.results.map(this.getMessageListItem);
    return (
      <div>
        <h4>Tratamentos</h4>
        <List>
          {listItems}
        </List>
      </div>
    )
  }
});

module.exports = TratamentoList;
