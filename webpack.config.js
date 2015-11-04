var path = require('path');
var webpack = require('webpack');
module.exports = {
    entry: [path.join(__dirname, 'app', 'scripts', 'iluminare.js')],
    output: {
        path: path.join(__dirname, 'app', 'static'),
        filename: 'bundle.js',
        publicPath: '/static/'
    },
    module: {
        loaders: [{
            //test: path.join(__dirname, 'app', 'js'),
            test: /(\.js)/,
            exclude: /node_modules/,
            loader: 'babel-loader'
        }]
    },
    resolve: {
        root: [path.join(__dirname, "bower_components")]
    },
    plugins: [
        new webpack.ResolverPlugin(
            new webpack.ResolverPlugin.DirectoryDescriptionFilePlugin("bower.json", ["main"])
        )
    ]
};
