exports.handler = function(context, event) {
    var request = JSON.parse(event.body);
    var sleep = process.env['SLEEP'] || 1000;

    context.logger.info('sink.handler begin')
    setTimeout(function() {
        context.logger.infoWith('sink.handler', { request })
        context.logger.info('sink.handler end')
        context.callback(event.body);
    }, sleep)
};