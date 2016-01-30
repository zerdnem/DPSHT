$(function(){

    var tpl = $('<li class="working"><input type="text" value="0" data-width="48" data-height="48"'+
        ' data-fgColor="#0087F7" data-readOnly="1" data-bgColor="#fff" /><p></p></li>');

    var ul = $('#upload ul');

    $('#drop a').click(function(){
        // Simulate a click on the file input button
        // to show the file browser dialog
        $(this).parent().find('input').click();
    });

    // Initialize the jQuery File Upload plugin
    $('#upload').fileupload({

        url: '/js',
        // This element will accept file drag/drop uploading
        dropZone: $('#drop'),

        // This function is called when a file is added to the queue;
        // either via the browse button, or via drag/drop:
        add: function (e, data) {


            // Append the file name and file size
            tpl.find('p').text(data.files[0].name)
                         .append('<i>' + formatFileSize(data.files[0].size) + '</i>');

            // Add the HTML to the UL element
            data.context = tpl.appendTo(ul);

            // Initialize the knob plugin
            tpl.find('input').knob();


            // Automatically upload the file once it is added to the queue
            var jqXHR = data.submit();
        },

        progress: function(e, data){

            // Calculate the completion percentage of the upload
            var progress = parseInt(data.loaded / data.total * 100, 10);

            // Update the hidden input field and trigger a change
            // so that the jQuery knob plugin knows to update the dial
            data.context.find('input').val(progress).change();

            if(progress == 100){
                data.context.removeClass('working');
            }
        },

        complete: function(e, data){

            var resp = e.responseText;

            var code = resp.split(":");

            if(code[0] === 'success') {
                $('span').remove();
                $('li').append('<span class="glyphicon glyphicon-ok">' + '</span>');
               // '<span class="badge"><a target="_blank" href="' + code[1] +'">' + code[2] + '</a></span><a>upload complete!</a>';
                console.log('success')
                }

            else if(code[0] === 'error' || code[0] === 'exists') {
                $('span').remove();
                $('li').append('<span class="glyphicon glyphicon-remove">' + '</span>');
                console.log('fail')
            }

/*            tpl.find('span').click(function(){

                if(tpl.hasClass('working')){
                    jqXHR.abort();
                }

                tpl.fadeOut(function(){
                    $('li').remove();
                });

            });*/

        },

        fail:function(e, data){
            // Something has gone wrong!
            data.context.addClass('error');
        },

    });

    // Prevent the default action when a file is dropped on the window
    $(document).on('drop dragover', function (e) {
        e.preventDefault();
    });

    // Helper function that formats the file sizes
    function formatFileSize(bytes) {
        if (typeof bytes !== 'number') {
            return '';
        }

        if (bytes >= 1000000000) {
            return (bytes / 1000000000).toFixed(2) + ' GB';
        }

        if (bytes >= 1000000) {
            return (bytes / 1000000).toFixed(2) + ' MB';
        }

        return (bytes / 1000).toFixed(2) + ' KB';
    }

});
