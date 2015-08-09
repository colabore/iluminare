
var React = require('react');
var MaterialUI = require('material-ui'),
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem;

var subscription;

var PacienteList = React.createClass({
  getInitialState: function() {
   return {'results': []};
  },
  componentDidMount: function() {
    subscription = this.props.searchByNameStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  _onTouchTap: function(e) {
    document.location = document.location.origin + '/#/paciente/details/' + e.currentTarget.id;
  },
  getMessageListItem: function(data) {
    return (
      <ListItem
        id={data.id}
        key={data.id}
        secondaryText={data.data_nascimento}
        onTouchTap={this._onTouchTap}>
        {data.nome}
      </ListItem>
    );
  },
  render: function() {
    var messageListItems = this.state.results.map(this.getMessageListItem);
    return (
      <List>
        {messageListItems}
      </List>
    )
  }
});

module.exports = PacienteList;
