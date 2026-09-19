// initialize name space for application global variables
var MyelnNotebooks = MyelnNotebooks || {};

function create_text_entry(itext) {
    var placeholder = $("#editor-body");
    placeholder.html('<textarea id="textarea"></textarea>');
    placeholder.data('kind', 'text');
    var simplemde = new SimpleMDE({
        autoDownloadFontAwesome: false,
        renderingConfig: {
            codeSyntaxHighlighting: true,
        },
        element: document.getElementById("textarea"),
        spellChecker: false,
        status: false,
        initialValue: itext,
        toolbar: [{
            name: "heading",
            action: SimpleMDE.toggleHeadingSmaller,
            className: "mi mi-type mi-md",
            title: "Heading"
        }, "|", {
            name: "bold",
            action: SimpleMDE.toggleBold,
            className: "mi mi-bold mi-md",
            title: "Bold"
        }, {
            name: "italic",
            action: SimpleMDE.toggleItalic,
            className: "mi mi-italic mi-md",
            title: "Italics"
        }, "|", {
            name: "quote",
            action: SimpleMDE.toggleBlockquote,
            className: "mi mi-quote mi-md",
            title: "Quote"
        }, "|", {
            name: "unordered-list",
            action: SimpleMDE.toggleUnorderedList ,
            className: "mi mi-list-ul mi-md",
            title: "Bullet List"
        }, {
            name: "ordered-list",
            action: SimpleMDE.toggleOrderedList ,
            className: "mi mi-list-ol mi-md",
            title: "Numbered List"
        }, "|", {
            name: "link",
            action: SimpleMDE.drawLink ,
            className: "mi mi-link mi-md",
            title: "Link"

        },"|", {
            name: "Equation (Latex Syntax)",
            action: wrapEquation,
            className: "mi mi-math mi-md",
            title: "Equation (latex syntax)",
        }, "|", {
            name: "undo",
            action: SimpleMDE.undo,
            className: "mi mi-undo mi-md",
            title: "Redo"
        }, {
            name: "redo",
            action: SimpleMDE.redo,
            className: "mi mi-redo mi-md",
            title: "Redo"
        }, "|", {
            name: "preview",
            action: togglePreview,
            className: "mi mi-eye mi-md no-disable",
            title: "Preview"
        }]
    });
    MyelnNotebooks.simplemde = simplemde;
    showEditor();
}

function create_sketch_entry(itext, ifile) {
    var placeholder = $("#editor-body");
    placeholder.data('kind', 'sketch');

    addSketchZone(placeholder);
    if (ifile) {
        load_sketch_bg(ifile);
    }

    addCaption(placeholder, itext);
    showEditor();
}

function create_image_entry(itext, ifile) {
    var placeholder = $("#editor-body");
    placeholder.data('kind', 'image');

    if (ifile) {
        addSketchZone(placeholder);
        load_sketch_bg(ifile);
    } else {
        addDropzone(placeholder, 'image');
    }
    addCaption(placeholder, itext);
    showEditor();
}

function create_file_entry(itext, ifile) {
    var placeholder = $("#editor-body");
    placeholder.data('kind', 'file');

    if (!ifile) {
        addDropzone(placeholder);
    }
    addCaption(placeholder, itext);
    showEditor();
}

function create_video_entry(itext, ifile) {
    var placeholder = $("#editor-body");
    placeholder.data('kind', 'video');

    if (ifile) {
        placeholder.append('<video width="100%" controls><source src="' +
            ifile.url + '" type="' + ifile.mime + '">Your browser does not support the video tag.</video>')
    } else {
        addDropzone(placeholder, 'video');
    }
    addCaption(placeholder, itext);
    showEditor();
}

function create_data_entry(itext) {
    var placeholder = $("#editor-body");
    placeholder.data('kind', 'data');

    var width = $('#entry-selector').width() - 2;
    var height = width / 3;
    var table_toolbar = (
        '<div class="editor-toolbar" id="table-toolbar">' +
        '<a title="Add Column" tabindex="-1" class="mi mi-add-col mi-md text-primary" id="table-add-col"></a>' +
        '<i class="separator">|</i>' +
        '<a title="Remove Column" tabindex="-1" class="mi mi-del-col mi-md text-danger" id="table-del-col"></a>' +
        '<i class="separator">|</i>' +
        '<a title="Add Row" tabindex="-1" class="mi mi-add-row mi-md text-primary" id="table-add-row"></a>' +
        '<i class="separator">|</i>' +
        '<a title="Remove Row" tabindex="-1" class="mi mi-del-row mi-md text-danger" id="table-del-row"></a>' +
        '</div>'
    );

    if (itext) {
        var table = placeholder.append(table_toolbar + '<div class="table-editable"></div>');
    } else {
        var table = placeholder.append(table_toolbar + '<div id="dropzone" class="table-editable"></div>');
        $('#dropzone').dropzone({
            url: placeholder.data('url'),
            autoProcessQueue: false,
            uploadMultiple: false,
            acceptedFiles: null,
            accept: function (file, done) {
                var read = new FileReader();
                read.readAsBinaryString(file);
                read.onloadend = function () {
                    if (file.type === 'text/csv') {
                        MyelnNotebooks.table.csv2JSON(read.result);
                    } else if (file.name.split('.').pop() === 'xdi') {
                        MyelnNotebooks.table.xdi2JSON(read.result);
                    }
                };
                if (this.files.length > 1) {
                    this.removeFile(this.files[0]);
                    done();
                }
            }
        });
    }

    MyelnNotebooks.table = $('.table-editable').myelnTable({
        'initial': itext
    });
    showEditor();
}

// Helper functions to implement sketcher toolbar
function set_sketch_mode(kind) {
    MyelnNotebooks.sketcher.mode = kind;
    $("[class*='btn-mode-']").removeClass('active');
    $('.btn-mode-' + kind).addClass('active');
}

function load_sketch_bg(file) {
    // for sketching on top of an image
    var canvas = $('canvas#sketcher')[0];
    var ctx = canvas.getContext('2d');
    var editor = $('#notebook-content');
    var img = new Image();
    img.onload = function() {
        var x = editor.width() - 32;
        var y = x * 4.5 / 9 - 2;
        var sx = img.width;
        var sy = img.height;
        if ((x / y) <= (sx / sy)) {
            var scale = x / sx;
            y = Math.max(y - (sy * scale), 0) / 2;
            x = 0
        } else {
            var scale = y / sy;
            x = Math.max(x - (sx * scale), 0) / 2;
            y = 0
        }
        ctx.drawImage(img, x, y, scale * sx, scale * sy);
    }
    img.src = file.url;
}


function showEditor() {
    var editor = $('#entry-editor');
    $('#entry-selector').slideUp(200);
    editor.slideDown(200, function(){
        this.scrollIntoView({
            alignToTop: false,
            behavior: "instant"
        });
    });

}

function closeEditor() {
    var editor = $('#entry-editor');
    var pk = editor.data('pk');
    editor.removeData('pk');
    var placeholder = $('#editor-body');

    $('#entry-selector').slideDown(200, function(){
        if (pk) {
            $('#entry-' + pk)[0].scrollIntoView({
                alignToTop: false,
                behavior: "smooth"
            });
        }
        editor.slideUp(200);
    });

    placeholder.empty();
    placeholder.removeClass('caption');
    MyelnNotebooks.myDropzone = null;
    MyelnNotebooks.sketcher = null;
    MyelnNotebooks.table = null;
}

function addDropzone(placeholder, kind) {
    var width = $('#entry-selector').width() - 2;
    var height = width / 3;
    placeholder.append('<div id="dropzone" class="border-bottom ' + kind + '" style="height: ' + height + 'px"></div>');

    $('#dropzone').dropzone({
        url: placeholder.data('url'),
        autoProcessQueue: false,
        uploadMultiple: false,
        acceptedFiles: kind && kind + '/*' || null,
        capture: 'camera',
        init: function () {
            var myDropzone = this;
            MyelnNotebooks.myDropzone = myDropzone;
        },
        accept: function (file, done) {
            if (this.files.length > 1) {
                this.removeFile(this.files[0]);
                done();
            }
        }
    });
}

function addSketchZone(placeholder) {
    placeholder.append('<canvas id="sketcher">');
    const width = $('#notebook-content').width()-2;
    const height = width * 4.5 / 9 - 2;
    const canvas = document.querySelector('#sketcher');
    const sketcher = new Atrament(canvas, {
        width: width,
        height: height,
    });
    MyelnNotebooks.sketcher = sketcher;

    placeholder.prepend('<div class="editor-toolbar sketcher-toolbar"></div>');
    sketcher.adaptiveStroke = false;

    var tb = $('.sketcher-toolbar');

    var tbbtn = [
        ['a', '', 'MyelnNotebooks.sketcher.clear();', 'Clear canvas', 'mi-trash'],
        ['|'],
        ['a', 'btn-mode-draw active', 'set_sketch_mode(`draw`);', "Draw", 'mi-pencil'],
        ['a', 'btn-mode-fill', 'set_sketch_mode(`fill`);', "Fill", 'mi-fill'],
        ['a', 'btn-mode-erase', 'set_sketch_mode(`erase`);', "Erase", 'mi-erase'],
        ['|'],
        ['a', 'active', 'MyelnNotebooks.sketcher.smoothing=!MyelnNotebooks.sketcher.smoothing; $(this).toggleClass(`active`);', 'Auto-smoothing', 'mi-activity'],
        ['a', '', 'MyelnNotebooks.sketcher.adaptiveStroke=!MyelnNotebooks.sketcher.adaptiveStroke; $(this).toggleClass(`active`);', 'Adaptive Stroke', 'mi-stroke'],
        ['|'],
        ['color', 'btn btn-link', 'MyelnNotebooks.sketcher.color=event.target.value;', 'Color', ''],
        ['|'],
        ['span', 'active', 'MyelnNotebooks.sketcher.weight=parseFloat(event.target.value);', 'Line width', 'mi-edit-line', '0.5', '40', '0.5', '0.5'],
        ['|'],
        ['span', '', 'MyelnNotebooks.sketcher.opacity=parseFloat(event.target.value);', 'Opacity', 'mi-star-half', '0', '1', '0.05', '1']
    ];

    //add buttons to toolbar
    $.each(tbbtn, function (i, data) {
        if (data[0] === '|') {
            var html = "<i class='separator'></i>";
        } else {
            if (data[0] === 'a') {
                var html = "<a title='{3}' onclick='{2}' tabindex='" + i + "' class='mi {1} mi-md {4}'></a>";
            } else if (data[0] === 'color') {
                var html = "<div id='colorPicker'><a class='color' title='{3}'><div class='colorInner'></div></a><div class='track'></div><input type='hidden' class='colorInput' value='#000000'/></div>";
            } else {
                var html = "<span class='mi {1} mi-md {4}' title='{3}'><input type='range' min='{5}' max='{6}' oninput='{2}' value='{8}' step='{7}'></span>";
            }
            $.each(data, function (k, v) {
                html = html.replace('{' + k + '}', v);
            });
        }
        tb.append(html);
    });

    var cp = $('#colorPicker');
    cp.tinycolorpicker();
    var picker = cp.data("plugin_tinycolorpicker");

    picker.setColor("#000000");
    cp.on('change', function(el, color) {
        sketcher.color=color;
    });

}

function addCaption(placeholder, itext) {
    placeholder.addClass('caption');
    placeholder.append('<textarea id="caption"></textarea>');
    var simplemde = new SimpleMDE({
        autoDownloadFontAwesome: false,
        element: document.getElementById("caption"),
        spellChecker: false,
        status: false,
        placeholder: "Add caption here...",
        initialValue: itext,
        toolbar: [{
            name: "bold",
            action: SimpleMDE.toggleBold,
            className: "mi mi-bold mi-md",
            title: "Bold"
        }, {
            name: "italic",
            action: SimpleMDE.toggleItalic,
            className: "mi mi-italic mi-md",
            title: "Italics"
        }, "|",{
            name: "link",
            action: SimpleMDE.drawLink ,
            className: "mi mi-link mi-md",
            title: "Link"

        },"|", {
            name: "Equation (Latex Syntax)",
            action: wrapEquation,
            className: "mi mi-math mi-md",
            title: "Equation (latex syntax)",
        }, "|", {
            name: "undo",
            action: SimpleMDE.undo,
            className: "mi mi-undo mi-md",
            title: "Redo"
        }, {
            name: "redo",
            action: SimpleMDE.redo,
            className: "mi mi-redo mi-md",
            title: "Redo"
        }, "|", {
            name: "preview",
            action: togglePreview,
            className: "mi mi-eye mi-md no-disable",
            title: "Preview"
        }]
    });
    MyelnNotebooks.simplemde = simplemde;
}

// SimpleMDE custom button functions
function togglePreview(editor) {
    SimpleMDE.togglePreview(editor);
    $('.editor-preview').each(function() {
        renderMathInElement(this);
    });
}

function wrapSelection(editor, delimeter) {

    var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();
    var text = selectedText || output;

    var startPoint = cm.getCursor("start");
    output = delimeter + text;
    cm.replaceSelection(output);

    var endPoint = cm.getCursor("end");
    cm.setSelection(startPoint, endPoint);
    cm.replaceSelection(output + delimeter);

    cm.setSelection(endPoint, endPoint);
    cm.focus();

}

function wrapEquation(editor) {
    return wrapSelection(editor, "$$")
}

function base64toFile(b64) {
    var base64 = b64.split(',')[1];

    var byteChars = atob(base64);
    var byteNums = new Array(byteChars.length);
    for (var i = 0; i < byteChars.length; i++) {
        byteNums[i] = byteChars.charCodeAt(i);
    }
    var byteArray = new Uint8Array(byteNums);
    var blob = new Blob([byteArray], {type: 'image/png'});
    var file = new File([blob], "sketch.png");
    return file;
}

function submitEntry() {
    var editor = $('#entry-editor');
    var placeholder = $("#editor-body");
    var entry_pk = editor.data('pk');
    var fd = new FormData();
    fd.append('kind', placeholder.data('kind'));
    if (entry_pk) {
        fd.append('pk', entry_pk);
    }

    var kind = placeholder.data('kind');
    if (MyelnNotebooks.simplemde) {
        fd.append('text', MyelnNotebooks.simplemde.value());
    }
    if (MyelnNotebooks.myDropzone) {
        fd.append('file', MyelnNotebooks.myDropzone.files[0]);
    } else if (MyelnNotebooks.sketcher) {
        var b64 = MyelnNotebooks.sketcher.toImage();
        fd.append('file', base64toFile(b64));
    } else if (MyelnNotebooks.table) {
        var table_json = MyelnNotebooks.table.exportJSON();
        fd.append('text', table_json);
    }

    // var last = $('.notebook-entry').last();
    // if (last) {
    //     fd.apend('last_shown', last.data('entry-pk'));
    // }


    $.ajax({
        type: "POST",
        url: placeholder.data("url"),
        data: fd,
        processData: false,
        contentType: false,
        encType: 'multipart/form-data',
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        },
        success: function (response) {
            if (entry_pk) {
                $('#entry-'+entry_pk + ' [title]').tooltip('hide');
                $('#entry-'+entry_pk).replaceWith(response);
                initEntries('#entry-'+entry_pk);
            } else {
                var newEntry = $(response);
                var entryDate = newEntry.data('entry-date');
                var sep = $('#notebook-content .page-separator[data-date="' + entryDate + '"]');

                if (sep.length === 0) {
                    var months = ["JAN.", "FEB.", "MAR.", "APR.", "MAY", "JUN.", "JUL.", "AUG.", "SEP.", "OCT.", "NOV.", "DEC."];
                    var parts = entryDate ? entryDate.split('-') : [];
                    var dateStr = "";
                    if (parts.length === 3) {
                        var mIdx = parseInt(parts[1], 10) - 1;
                        var day = parseInt(parts[2], 10);
                        dateStr = months[mIdx] + " " + day + ", " + parts[0];
                    } else {
                        var now = new Date();
                        dateStr = months[now.getMonth()] + " " + now.getDate() + ", " + now.getFullYear();
                    }
                    var sepElem = $('<li class="page-separator" data-date="' + entryDate + '" id="separator-' + entryDate + '"><div class="date px-4 text-center">' + dateStr + '</div></li>');
                    var targetList = $('#notebook-content ul.entry-page').last();
                    if (targetList.length === 0) {
                        targetList = $('<ul class="list-unstyled my-0 entry-page current-page"></ul>').appendTo('#notebook-content');
                    }
                    targetList.append(sepElem);
                    targetList.append(newEntry);
                } else {
                    var entriesForDate = $('#notebook-content .notebook-entry[data-entry-date="' + entryDate + '"]');
                    if (entriesForDate.length > 0) {
                        entriesForDate.last().after(newEntry);
                    } else {
                        sep.after(newEntry);
                    }
                }
                initEntries(newEntry);
            }
            closeEditor();
        }
    });
}

function deleteEntry(elem){
    var button = $(elem);
    var entry = button.closest('.notebook-entry');
    var entry_id = entry.data('entry-pk');

    if (button.is('.text-danger')) {
		$.ajax({
			type: 'POST',
			url: button.data('url'),
            data: {'pk': entry_id},
			beforeSend: function(xhr, settings){
			    button.popover('hide');
				xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
			},
			success: function() {
			    button.popover('hide');
			    $('#entry-'+entry_id + ' [data-original-title]').tooltip('dispose');
                var entryDate = entry.data('entry-date');
                entry.remove();
                if (entryDate) {
                    var remaining = $('#notebook-content .notebook-entry[data-entry-date="' + entryDate + '"]');
                    if (remaining.length === 0) {
                        $('#notebook-content .page-separator[data-date="' + entryDate + '"]').remove();
                    }
                }
                var last_page = $('ul.entry-page').last();
                if (last_page.find('.notebook-entry').length === 0) {
                    last_page.remove();
                }
            },
            error: function() {
			    button.shake();
            }
		});
    } else {
        button.addClass("text-danger");
        button.popover({
            placement: 'right',
            title: "Are you sure?",
            content: "Click again to confirm!"
        });
        button.popover('show');
        setTimeout(function () {
            button.removeClass('text-danger');
            button.popover('hide');
        }, 2000);
    }
}

function prepare_editor(pk) {
    var editor = $("#entry-editor");
    if (editor.is(':visible')) {
        closeEditor();
    }
    editor.data('pk', pk);
}


function edit_text_entry(pk) {
    prepare_editor(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_text_entry(data.text);
    }, 'json');
}
function edit_sketch_entry(pk) {
    prepare_editor(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_sketch_entry(data.text, data.file);
    }, 'json');
}
function edit_image_entry(pk) {
    prepare_editor(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_image_entry(data.text, data.file);
    }, 'json');
}
function edit_file_entry(pk) {
    prepare_placeholder(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_file_entry(data.text, data.file);
    }, 'json');
}
function edit_video_entry(pk) {
    prepare_editor(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_video_entry(data.text, data.file);
    }, 'json');
}
function edit_data_entry(pk) {
    prepare_editor(pk);
    $.get('/entry/'+pk+'/', function(data, status) {
        create_data_entry(data.text);
    }, 'json');
}

//tables
(function ( $ ) {
    $.fn.myelnTable = function (options) {

        var table = $(this);
        var selectedRow = null;
        var selectedCol = null;
        var toolbar = $('#table-toolbar');

        buildTable(options['initial']);

        function colName(num) {
            for (var ret = '', a = 1, b = 26; (num -= a) >= 0; a = b, b *= 26) {
                ret = String.fromCharCode(parseInt((num % b) / a) + 65) + ret;
            }
            return ret;
        }
        function renumberRows() {
            $('tbody tr').each(function(){
                $(this).find('th.row-index').html($(this).index() + 1);
            });
        }

        function renameHeaders() {
            table.find('thead th.header').each(function(){

            });
        }
        function caret(event) {
            var _range = document.getSelection().getRangeAt(0);
            var range = _range.cloneRange();
            range.selectNodeContents(event.target);
            range.setEnd(_range.endContainer, _range.endOffset);
            return range.toString().length;
        }

        function addRow () {
            var rows = table.find('tbody tr');
            var clone_index;
            if (selectedRow !== null) {
                clone_index = selectedRow;
            } else {
                clone_index = rows.length - 1
            }
            var to_clone = rows.eq(clone_index);
            var clone = to_clone.clone(true);
            clone.find('td').html("");
            to_clone.after(clone);
            renumberRows();
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
        }

        function addCol () {
            var clone_index = selectedCol || (table.find('thead tr th').length - 1);
            var to_clone = table.find('thead tr th').eq(clone_index);
            var new_col = to_clone.clone(true);
            new_col.html(colName(clone_index + 1));
            to_clone.after(new_col);
            table.find('tbody tr').each(function () {
                var to_clone = $(this).find('td, th').eq(clone_index);
                var new_col = to_clone.clone(true);
                new_col.html("");
                to_clone.after(new_col)

            });
            table.find('colgroup').eq(clone_index).after($("<colgroup></colgroup>"));
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
        }

        function removeCol () {
            var cols = table.find('colgroup');
            if ((selectedCol !==  null) && (cols.length > 2)) {
                table.find('tr').each(function () {
                    row = $(this);
                    row.find('td, th').eq(selectedCol).remove();
                });
                cols.eq(selectedCol).remove();
            }
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
        }
        function removeRow () {
            var rows = table.find('tbody tr');
            if ((selectedRow !== null) && (rows.length > 1)) {
                rows.eq(selectedRow).remove();
            }
            renumberRows();
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
        }


        toolbar.on('click', '#table-add-row', addRow);
        toolbar.on('click', '#table-del-row', removeRow);
        toolbar.on('click', '#table-add-col', addCol);
        toolbar.on('click', '#table-del-col', removeCol);


        table.on('click', 'thead th.header', function(e){
            var colIndex = $(e.target).index();
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
            table.find('colgroup').eq(colIndex).addClass('selected');
            selectedCol = colIndex;
        });

        table.on('click', 'tbody td', function(e){
            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
            selectedCol = null;
            selectedRow = null;
        });

        table.on('click', 'tbody th.row-index', function(e){

            table.find('colgroup.selected').removeClass('selected');
            table.find('tr.selected').removeClass('selected');
            var row =  $(this).closest('tr');
            row.addClass('selected');
            selectedRow = row.index();
        });

        function setupRowNav () {
            table.on('keydown', 'tbody td', function (e) {
                if (e.which == 13) {
                    e.preventDefault();
                    var new_line = $(this).closest('tr').next().find('td');
                    if (!new_line.length) {
                        addRow();
                        new_line = table.find('tr').last().find('td');
                    }
                    new_line[0].focus();
                } else if (e.which == 9) {
                    var new_line = $(this).closest('tr').next().find('td');
                    var num_cols = $(this).parent().children().length - 2;
                    if (!new_line.length && ($(this).index() === num_cols)) {
                        addRow();
                        new_line = table.find('tr').last().find('td');
                    }
                } else if (e.which == 40) {
                    //down arrow
                    var cur_row = $(this).closest('tr');
                    var ccol_index = $(this).index();
                    var next_row = cur_row.next();

                    if (next_row.length > 0) {
                        e.preventDefault();
                        next_row.find('th, td').eq(ccol_index).focus();
                    }
                } else if (e.which == 38) {
                    //up arrow
                    var cur_row = $(this).closest('tr');
                    var ccol_index = $(this).index();
                    var prev_row = cur_row.prev();

                    if (prev_row.length > 0) {
                        e.preventDefault();
                        prev_row.find('th, td').eq(ccol_index).focus();
                    }
                } else if (e.which == 39) {
                    //right
                    if (caret(e) === $(e.target).text().length) {
                        var next_cell = $(this).next('td');
                        if (next_cell.length > 0) {
                            e.preventDefault();
                            next_cell.focus();
                        }
                    }

                } else if (e.which == 37 ) {
                    //left arrow
                    if (caret(e) === 0) {
                        var prev_cell = $(this).prev('td');
                        if (prev_cell.length > 0) {
                            e.preventDefault();
                            prev_cell.focus();
                        }
                    }
                }
            });
        }

        // A few jQuery helpers for exporting only
        jQuery.fn.pop = [].pop;
        jQuery.fn.shift = [].shift;

        this.exportJSON = function exportTable () {
            var rows = table.find('thead .header');
            var data = {'headers': []};
            var info = {};

            // Get the headers (add special header logic here)
            //$(rows.shift()).find('th:not(:empty)').each(function () {
            table.find('thead .header').each(function (i) {
                var col_name = colName(i);
                var h = $(this).text().trim() || col_name;
                data['headers'].push(h);
                info[i] = [];
            });

            table.find('tbody tr').each(function (i) {
                if (i <= 1000) {  // Maximum 1000 rows
                    $(this).find('td').each(function(j) {
                        if (j <= 10) { // Maximum 10 columns
                            var value = parseFloat($(this).text()) || $(this).text().trim();
                            info[j].push(value);
                        }
                    });
                }
            });

            data['data'] = info;

            // Output the result
            return JSON.stringify(data);

        };

        this.csv2JSON = function csv2JSON (csv) {
            //var csv is the CSV file with headers
            var rawData = Papa.parse(csv);
            var headers = rawData.data[0].slice(0, 10); // Maximum 10 columns

            var result = {"headers": headers, "data": {}};

            for(var i=1;i< Math.min(rawData.data.length, 1000);i++){
                if (rawData.data[i].length >= headers.length) {
                    for(var j=0;j<headers.length;j++){
                        if (i === 1) {
                            result["data"][j] = [];
                        }
                        result["data"][j].push(rawData.data[i][j]);
                    }
                }

            }

            //JavaScript object
            var details = JSON.stringify(result);
            buildTable(details);
        };

        this.xdi2JSON = function xdi2JSON (xdi) {
            //var xdi is the XDI file with headers
            var lines = xdi.split("\n");
            var meta = [];
            var data = {};
            for (i = 0; i < Math.min(1000, lines.length); i++ ) { // Maximum 1000 lines processed
                if (lines[i][0] === '#') {
                    meta.push(lines[i]);
                } else {
                    break;
                }
            }
            lines.splice(0, i);
            var headers_full = meta.pop().match(/\S+/g);
            headers_full.shift();
            var headers = headers_full.slice(0, 10);  //Maximum 10 columns
            for (i = 0; i < lines.length; i++ ) {
                var currentline = $.trim(lines[i]).match(/\S+/g);
                for (var j = 0; j < headers.length; j++) {
                    if (i === 0) {
                        data[j] = [];
                    }
                    data[j].push(currentline[j]);
                }
            }
            var details = JSON.stringify({"headers": headers, "data": data});
            buildTable(details);
        };

        function buildTable (details) {
            table.empty();
            if (details) {
                // define an existing table
                var data = JSON.parse(details);
            } else {
                // define a default table
                var data = {
                    'headers': ['A', 'B', 'C', 'D'],
                    'data': {0:[""], 1:[""], 2:[""], 3:[""]}
                }
            }
            var table_toolbar = ("");

            var table_template = _.template(
                '<table class="table table-sm">' +
                '   <colgroup></colgroup>' +
                '   <% _.each(headers, function(header, i){ %>' +
                '   <colgroup></colgroup>' +
                '   <%  }); %>' +
                '   <colgroup></colgroup>' +
                '   <thead>' +
                '   <tr>' +
                '       <th></th>' +
                '       <% _.each(headers, function(header, i) { %>' +
                '           <th class="header" contenteditable="true"><%= headers[i] %></th>' +
                '       <% }); %>' +
                '   </tr>' +
                '   </thead>' +
                '   <tbody class=".sortable">' +
                '   <% for (var i=0; i < data[0].length; i++) { %>' +
                '       <tr>' +
                '           <th class="row-index"><%= (i+1) %></th>' +
                '           <% for (var h=0; h < headers.length; h++) { %>' +
                '              <td contenteditable="true"><%= data[h][i] %></td>' +
                '           <% } %>' +
                '       </tr>' +
                '   <% } %> ' +
                '   </tbody>' +
                '</table>'
            );
            table.prepend(table_toolbar);
            table.append(table_template(data));
            sortable('.table-editable tbody', {
                forcePlaceholderSize: true,
                handle: 'th:first-child',
                items: 'tr'
            })[0].addEventListener('sortupdate', renumberRows);
            setupRowNav();
        }

        return this;
    };
}(jQuery));

(function ( $ ) {
    $.fn.myelnCalendar = function (options ) {

        // Default
        var settings = $.extend({
            target: "#calendar-target",
            currentMonth: moment().format('YYYY-MM-DD'),
        }, options );

        // configure the target to receive content
        var target = $(settings.target);
        var contents = target.find('div.contents');
        var calendar_template = (
            '<div id="notebook-clndr">' +
            '    <script id="notebook-clndr-template" type="text/template">' +
            '        <div class="clndr-previous-button no-select"><i class="mi mi-chevron-left"></i></div>' +
            '        <div class="control">' +
            '            <div class="month"><%= month %></div>' +
            '            <div class="year"><%= year %></div>' +
            '        </div>' +
            '        <div class="days-container">' +
            '           <div class="days">' +
            '               <div class="headers">' +
            '                   <% _.each(daysOfTheWeek, function(day) { %>' +
            '                   <div class="day-header"><%= day %></div>' +
            '                   <% }); %>' +
            '               </div>' +
            '               <% _.each(days, function(day) { %>' +
            '               <div class="<%= day.classes %>"><%= day.day %></div>' +
            '               <% }); %>' +
            '           </div>' +
            '        </div>' +
            '        <div class="control">' +
            '            <div class="month"><a href="' + settings.selectTarget + '" id="clndr-default-link">' +
            '               <i class="mi mi-arrow-right-circle"></i> <span class="pb-1">Latest</span></a>' +
            '           </div>' +
            '        </div>' +
            '        <div class="clndr-next-button no-select"><i class="mi mi-chevron-right"></i></div>' +
            '    </script>' +
            '</div>'
        );


        // setup events
        this.click(function () {
            contents.html(calendar_template);
            var months_fetched = {};

            function fetchEvents(month) {

                var months = [moment(month).subtract(1, 'month'), month, moment(month).add(1, 'month')];
                var months_to_fetch = [];

                $.each(months, function(i, item){
                    var key = item.format('YYYYMM');
                    if (! months_fetched[key]) {
                        months_to_fetch.push(key);
                    }
                });

                if (months_to_fetch.length) {
                    $.ajax({
                        type: 'GET',
                        dataType: 'json',
                        url: settings.eventSource,
                        data: {
                          months: months_to_fetch.join()
                        },
                        success: function(response) {
                          clndr.addEvents(response);
                          $.each(months_to_fetch, function(i, item){
                              months_fetched[item] = true;
                          });
                        }
                    });
                }

            }

            var clndr = $('#notebook-clndr').clndr({
                template: $('#notebook-clndr-template').html(),
                startWithMonth: settings.currentMonth,
                weekOffset: 1,
                clickEvents: {
                    click: function(e) {
                        if (e.events.length) {
                            window.location.search = 'date=' + e.date.format('YYYY-MM-DD');
                        }
                    },
                    onMonthChange: fetchEvents
                },
                adjacentDaysChangeMonth: true,
                forceSixRows: true
            });
            fetchEvents(moment(settings.currentMonth, "YYYY-MM-DD"));
            target.slideDown(200);
            target.focus();
        });
    };

}(jQuery));

function getSelectionText() {
    var text = "";
    if (window.getSelection) {
        text = window.getSelection().toString();
    } else if (document.selection && document.selection.type != "Control") {
        text = document.selection.createRange().text;
    }
    return text;
}

//comments
(function($){
    $.fn.annotate = function(entry_selector, options) {
        var settings = $.extend({
            url: $(this).data('annotate-url'),
        }, options );

        var eventData = {};
        var html = $('html');
        html.data('annotate-url', settings.url); // Keep for later
        var selector = entry_selector + ' > *';
        var highlight_mark = entry_selector + ' mark.highlight';

        // prepare and emit "myeln:annotate" event on notebook entry nodes
        $(this).on('mousedown touchstart', selector + ', ' + highlight_mark, function(e){
            eventData.x0 = e.clientX;
            eventData.y0 = e.clientY;
            if ($(this).is('mark.highlight')) {
                eventData.start_mark = this;
                return true;
            }

        });
        $(this).on('mouseup touchend', selector + ', ' + highlight_mark, function(e){
            eventData.x1 = e.clientX;
            eventData.y1 = e.clientY;
            eventData.selection = getSelectionText().trim();
            if ($(this).is('mark.highlight')) {
                eventData.end_mark = this;
                eventData.within_mark = (eventData.start_mark === eventData.end_mark) && (eventData.start_mark !== null);
                return true;
            }
            eventData.node = $(this);

            if (eventData.selection) {
                var o = eventData.node.offset();
                var w = eventData.node.width();
                var h = eventData.node.height();
                var xe = (eventData.x1 + eventData.x0)/2 + html.scrollLeft();
                var ye = Math.max(eventData.y1, eventData.y0, h) + 20 + html.scrollTop();
                var pos = {
                    x: Math.max(-w/2, Math.min(100*(xe - (o.left + w/2))/w, w/2)),
                    y: (ye - o.top)*100/h - 100
                };

                $(this).trigger({
                    type: "myeln:annotate",
                    offset: pos.x + '%, ' + pos.y + '%',
                    x: pos.x,
                    y: pos.y,
                    selection: eventData.selection,
                    highlighted: eventData.within_mark,
                });
                eventData = {};
            }
        });
        $(document).on("myeln:annotate", selector, function(e) {
            var node = $(this);
            var hideHighlight = Boolean(e.highlighted);
            node.popover({
                trigger: "click",
                html: true,
                container: 'body',
                placement: "bottom",
                offset: e.offset,
                fallbackPlacement: ['top'],
                boundary: 'window',
                content: _.template(
                    '<ul class="list-unstyled annotation-menu m-0">' +
                    '   <li onclick="addComment();" title="Comment">' +
                    '       <i class="mi mi-comment mi-fw"></i>' +
                    '   </li>' +
                    '<% if (showHighlight) { %>' +
                    '   <li onclick="addHighlight();" title="Highlight">' +
                    '       <i class="mi mi-highlighter mi-fw"></i>' +
                    '   </li>' +
                    '<% } %>' +
                    '</ul>'
                )({showHighlight: !hideHighlight}),
                template: (
                    '<div class="popover menu" role="tooltip">' +
                    '   <div class="popover-arrow arrow"></div>' +
                    '   <h3 class="popover-header"></h3>' +
                    '   <div class="popover-body"></div>' +
                    '</div>'
                )
            });
            node.popover("show");

            // Save annotation parameters to window
            MyelnNotebooks.annotation = {
                pk: null,
                node: node,
                method: 'create',
                index: node.index(),
                entry_id: node.parent().data('entry-pk'),
                offset: e.offset,
                selection: e.selection,
                type: 'highlight',
                url: settings.url
            };

        });

        $(document).on("myeln:unannotate", "mark", function() {
            if (MyelnNotebooks.annotation != null) {
                return
            }
            var node = $(this);
            var menu = "";
            if ($(this).data('editable')){
                menu = (
                    '<ul class="list-unstyled annotation-menu m-0">' +
                    '   <li class="undo" onclick="delHighlight();" title="unhighlight">' +
                    '       <i class="mi mi-highlighter mi-fw"></i>' +
                    '   </li>' +
                    '</ul>'
                );
            } else {
                menu = (
                    '<ul class="list-unstyled annotation-menu m-0">' +
                    '   <li>' + $(this).data('author') + '   </li>' +
                    '</ul>'
                );
            }
            node.popover({
                trigger: "click",
                html: true,
                container: 'body',
                placement: "bottom",
                fallbackPlacement: ['top'],
                boundary: 'window',
                content: menu,
                template: (
                    '<div class="popover menu" role="tooltip">' +
                    '   <div class="popover-arrow arrow"></div>' +
                    '   <h3 class="popover-header"></h3>' +
                    '   <div class="popover-body"></div>' +
                    '</div>'
                )
            });
            node.popover("show");

            // Save annotation parameters to window
            MyelnNotebooks.annotation = {
                node: node,
                index: null,
                method: 'remove',
                pk: node.data('pk'),
                entry_id: node.closest(entry_selector).data('entry-pk'),
                selections: node.text(),
                type: 'highlight',
                url: settings.url
            };

        });

        // close popup menu on next click outside
        $(document).on('mousedown touchstart', function (e) {
            if (MyelnNotebooks.annotation) {
                var nodeEl = MyelnNotebooks.annotation.node[0];
                var popover = (window.bootstrap && bootstrap.Popover ? bootstrap.Popover.getInstance(nodeEl) : null) || MyelnNotebooks.annotation.node.data('bs.popover');
                if (popover) {
                    var popoverTip = popover.tip || (popover.getTipElement ? popover.getTipElement() : null) || popover;
                    if (!$(popoverTip).is(e.target) && $(popoverTip).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                        MyelnNotebooks.annotation.node.popover('dispose');
                        MyelnNotebooks.annotation = null;
                    }
                }
            }
        });

        $(document).on('click', 'mark.highlight', function(){
            $(this).trigger('myeln:unannotate');
        });
    };
})(jQuery);


function addComment() {
    var template = (
        '<div class="comment-form" tabindex="-1">' +
        '    <textarea id="comment-input" rows="6" cols="30" name="text" ' +
        '       class="form-control input-md" placeholder="Add your comments ..."></textarea>' +
        '    <div class="w-100 comment-form-tools">' +
        '       <i class="mi mi-comments mi-fw"></i>' +
        '       <button type="button" title="Cancel" onclick="cancelComment();" class="btn btn-sm btn-light ml-auto mr-2"><i class="mi mi-cross"></i>' +
        '       </button>' +
        '       <button type="button" title="Save" onclick="submitComment();" class="btn btn-sm btn-success"><i class="mi mi-save mi-fw"></i>' +
        '       </button>' +
        '   </div>' +
        '</div>' +
        ''
    );
    if (MyelnNotebooks.annotation) {
        var annotation = MyelnNotebooks.annotation;
        annotation.node.popover('dispose');

        // show comment form
        annotation.type = 'comment';
        annotation.node.popover({
            trigger: "click",
            html: true,
            container: 'body',
            placement: "bottom",
            fallbackPlacement: ['top'],
            offset: annotation.offset,
            content: template,
            template: (
                '<div class="popover form menu" role="tooltip">' +
                '   <div class="popover-arrow arrow"></div>' +
                '   <h3 class="popover-header"></h3>' +
                '   <div class="popover-body"></div>' +
                '</div>'
            )
        });
        annotation.node.popover('show');
        annotation.node.mark(annotation.selection, {
            caseSensitive: true,
            ignoreJoiners: true,
            className: annotation.type,
            acrossElements: true,
            separateWordSearch: false,
            "each": function(mark) {
                if (!($(mark).text().replace(/\s/g, '').length)) {
                    $(mark).css('display', 'none');
                }
            }
        });
    }
    $('#comment-input').focus();
}

function addHighlight() {
    if (MyelnNotebooks.annotation) {
        var annotation = MyelnNotebooks.annotation;
        annotation.node.popover('dispose');
        annotation.node.mark(annotation.selection, {
            caseSensitive: true,
            ignoreJoiners: true,
            className: 'highlight',
            acrossElements: true,
            separateWordSearch: false
        });
        submitAnnotation();
    }
}

function delHighlight() {
    if (MyelnNotebooks.annotation) {
        submitAnnotation();
    }
}

function delComment(pk) {
    var item = JSON.parse($('#annotation-'+pk).text());
    MyelnNotebooks.annotation = {
        node: null,
        index: item.node,
        method: 'remove',
        pk: item.id,
        entry_id: item.entry_id,
        selections: "",
        type: 'comment',
        url: $('html').data('annotate-url'),
    };
    submitAnnotation();
}

function cancelComment(){
    if (MyelnNotebooks.annotation) {
        var annotation = MyelnNotebooks.annotation;
        annotation.node.popover('dispose');
        MyelnNotebooks.annotation = null;
        annotation.node.unmark({className:'comment'});
    }
}

function submitComment() {
    if (MyelnNotebooks.annotation) {
        var annotation = MyelnNotebooks.annotation;
        annotation.text = $('#comment-input').val();

        // exit if not text provided for comment types
        annotation.node.popover('dispose');
        if (annotation.type === 'comment' && !annotation.text ) {
            MyelnNotebooks.annotation = null;
            annotation.node.unmark();
        } else {
            submitAnnotation();
        }
    }
}

function submitAnnotation() {
    if (MyelnNotebooks.annotation) {
        var annotation = MyelnNotebooks.annotation;

        $.ajax({
			type: 'POST',
			url: annotation.url,
            data: {
			    'pk': annotation.pk,
			    'entry_id': annotation.entry_id,
                'kind': annotation.type,
                'selection': annotation.selection,
                'index': annotation.index,
                'text': annotation.text,
                'method': annotation.method
            },
			beforeSend: function(xhr, settings){
			    if (annotation.node) {
			        annotation.node.popover('dispose');
                }
                MyelnNotebooks.annotation = null;
				xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
			},
			success: function(response) {
			    var selector = '#entry-'+annotation.entry_id;
			    $(selector + ' [data-original-title]').tooltip('dispose');
                $(selector).replaceWith(response);
                initEntries(selector);
            }
		});
    }
}


function markAnnotations(selector){
    $(selector).each(function(){
        const entry = $(this);
        //highlights
        let highlights = [];
        entry.find('.annotations > script.highlight-annotation').each( function() {
            let item = JSON.parse($(this).text());
            item.isAuthor = $(this).data('isauthor');
            highlights.push(item);
        });

        //mark each one
        $.each(highlights, function(i, item){
            const node = entry.children().eq((item.node));
            if (node) {
                node.mark(item.selections,{
                    caseSensitive: true,
                    ignoreJoiners: true,
                    className: 'highlight',
                    acrossElements: true,
                    separateWordSearch: false,
                    each: function(mark) {
                        $(mark).attr('data-pk', item.id);
                        $(mark).attr('data-editable', item.isAuthor);
                        $(mark).attr('data-author', item.author);
                        if (!($(mark).text().replace(/\s/g, '').length)) {
                            $(mark).css('display', 'none');
                        }
                    }
                });
            }
        });

        //comments
        const comments_template = _.template(
            '<div class="node-comments dropdown-menu">' +
            '    <% _.each(comments, function(comment) { %>' +
            '    <div class="comments-content" data-pk="<%= comment.id %>" onmouseenter="markComment(this);" onmouseleave="unmarkComment(this);">' +
            '       <div class="comment-header w-100">' +
            '           <strong><%= comment.author %></strong>' +
            '           <span><%= comment.time %></span>' +
            '       </div>' +
            '       <div class="comment-body"><%= comment.text %></div>' +
            '       <% if (comment.isAuthor) { %> ' +
            '       <div href="#!" class="comment-delete w-100">' +
            '           <i class="mi mi-cross" onclick="delComment(<%= comment.id %>);"></i>' +
            '       </div>' +
            '       <% } %>' +
            '    </div>' +
            '    <% }); %>' +
            '</div>'
        );

        entry.children().each(function (){
            const node = $(this);
            let items = [];
            entry.find('.annotations > script.comment-'+node.index()).each(function(){
                let item = JSON.parse($(this).text());
                item.isAuthor = $(this).data('isauthor');
                items.push(item);
            });

            if (items.length) {
                node.append($(
                    '<div class="comment-mark ignore-selects">' +
                    '   <span class="mi-stack mi-2x">' +
                    '       <i class="mi mi-comment-alt mi-stack-2x bubble"></i>' +
                    '       <strong class="mi-stack-1x mi-inverse">'+items.length+'</strong>' +
                    '   </span>' +
                    comments_template({
                        comments: items
                    }) +
                    '</div>'
                ));
            }
        });
    });
}

function markComment(element) {
    var data = JSON.parse($('#annotation-'+$(element).data('pk')).text())
    var node = $(element).closest('.notebook-entry').children().eq((data.node));
    if (node) {
        node.mark(data.selections,{
            "caseSensitive": true,
            "ignoreJoiners": true,
            "className": 'comment',
            "acrossElements": true,
            "separateWordSearch": false,
            "each": function(mark) {
                if (!($(mark).text().replace(/\s/g, '').length)) {
                    $(mark).css('display', 'none');
                }
            }
        });
    }
}

function unmarkComment(element) {
    var data = JSON.parse($('#annotation-'+$(element).data('pk')).text())
    var node = $(element).closest('.notebook-entry').children().eq((data.node));
    if (node) {
        node.unmark({
            "className": 'comment',
        });
    }
}


//tags
function editTags(elem){
    var content = $('#notebook-content');
    var button = $(elem);
    var entry = button.closest('.notebook-entry');
    var initial = button.data('tags');

    MyelnNotebooks.tags = {
        entry_id: entry.data('entry-pk'),
        url: button.data('url'),
    };

    var width = Math.max($(content).width(), 300) * ( 0.8);

    var template = (
        '<div class="comment-form" tabindex="-1">' +
        '    <textarea id="tag-input" rows="3" cols="30" name="text" ' +
        '       class="form-control input-md" ' +
        '       placeholder="Enter comma-separated list of keywords ...">' + initial + '</textarea>' +
        '    <div class="w-100 comment-form-tools">' +
        '       <i class="mi mi-tags mi-fw"></i>' +
        '       <button type="button" title="Cancel" onclick="cancelTags();" class="btn btn-sm btn-light ml-auto mr-3"><i class="mi mi-cross"></i>' +
        '       </button>' +
        '       <button type="button" title="Save" onclick="submitTags();" class="btn btn-sm btn-success"><i class="mi mi-save"></i>' +
        '       </button>' +
        '    </div>' +
        '</div>' +
        ''
    );

    MyelnNotebooks.popover = button.popover({
        trigger: "click",
        html: true,
        container: 'body',
        placement: "bottom",
        fallbackPlacement: ['top'],
        content: template,
        template: (
            '<div class="popover form menu" role="tooltip">' +
            '   <div class="popover-arrow arrow"></div>' +
            '   <div class="popover-body"></div>' +
            '</div>'
        )
    });

    button.popover("show");
    $('#tag-input').focus();

}

function cancelTags() {
    if (MyelnNotebooks.popover) {
        var button = MyelnNotebooks.popover;
        button.popover('dispose');
        MyelnNotebooks.popover = null;
        MyelnNotebooks.tags = null;
    }
}

function submitTags() {
    if (MyelnNotebooks.tags) {
        var tags = MyelnNotebooks.tags;
        var text = $('#tag-input').val();

        if (!text ) {
            MyelnNotebooks.popover.popover('dispose');
            MyelnNotebooks.popover = null;
            MyelnNotebooks.tags = null;
            return
        }

        $.ajax({
			type: 'POST',
			url: tags.url,
            data: {
			    'pk': tags.entry_id,
                'tags': text,
            },
			beforeSend: function(xhr, settings){
                MyelnNotebooks.popover.popover('dispose');
                MyelnNotebooks.popover = null;
                MyelnNotebooks.tags = null;
				xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
			},
			success: function(response) {
			    var selector = '#entry-'+tags.entry_id;
			    $(selector + ' [data-original-title]').tooltip('dispose');
                $(selector).replaceWith(response);
                initEntries(selector);
            }
		});
    }
}


function loadPage(element, dir, scroll, pk) {
    scroll = scroll || false;
    var container = $('#notebook-content');
    var url = $(element).data('page-url');
    if (!url) {
        var anchor = (dir === 'prev') ? $(element).find('.notebook-entry').first() : $(element).find('.notebook-entry').last();
        url = anchor.data('page-url');
    }
    if (!url) {
        var anchor = (dir === 'prev') ? $('.notebook-entry').first() : $('.notebook-entry').last();
        url = anchor.data('page-url');
    }
    if (!url) {
        MyelnNotebooks.loading = false;
        return;
    }

    $.ajax({
        type: 'GET',
        url: url,
        data: {
            'load': dir,
        },
        success: function(response, status, xhr) {
            if (xhr.status === 204 || !response || $.trim(response) === '') {
                MyelnNotebooks.loading = false;
                return;
            }
            var newContent = $(response);
            if (newContent.length === 0) {
                MyelnNotebooks.loading = false;
                return;
            }

            if ((dir === 'next') || (dir === 'rest')) {
                // If appending, remove duplicate date separators already present above
                newContent.find('.page-separator').each(function() {
                    var d = $(this).data('date');
                    if (d && container.find('.page-separator[data-date="' + d + '"]').length > 0) {
                        $(this).remove();
                    }
                });
                container.append(newContent);
            } else {
                // Prepending: remove existing date separators that are now inside the date span
                newContent.find('.page-separator').each(function() {
                    var d = $(this).data('date');
                    if (d) {
                        var existingSep = container.find('.page-separator[data-date="' + d + '"]');
                        if (existingSep.length > 0) {
                            existingSep.remove();
                        }
                    }
                });
                var firstElem = container.children().first();
                var height = 0;
                container.prepend(newContent);
                firstElem.prevAll().each(function(){
                    height += $(this).outerHeight();
                });
                $('main').scrollTop($('main').scrollTop() + height);
            }
            if (scroll) {
                $('.notebook-entry').last()[0].scrollIntoView({
                    alignToTop: false,
                    behavior: "smooth"
                });
            }
            MyelnNotebooks.loading = false;
            initEntries(newContent.find('.notebook-entry').addBack('.notebook-entry'));
        },
        error: function() {
            MyelnNotebooks.loading = false;
        }
    });
}


function loadIndex(element, height) {
    var active = $('#notebook-index #index-' + element.data("entry-pk"));
    var index = $('#notebook-index .index');

    $('#notebook-index .active').removeClass('active');
    active.addClass('active');

    var num_visible = Math.round(height / 50);

    if (!MyelnNotebooks.index_loading) {
        $.ajax({
            type: 'GET',
            url: element.data('index-url'),
            data: {
                'load': num_visible,
                'active': element.data("entry-pk")
            },
            success: function(response) {
                var source = $('' + response + '');
                var index = $('#notebook-index .index');

                var end = false;
                var first_entry = index.children().first();
                $(source).children().each(function() {
                    var el = $(index).find('#index-' + $(this).data('entry-pk'));
                    if (el.length) {
                        end = true;
                    } else {
                        if (!end) {
                            first_entry.before($(this));
                        } else {
                            index.append($(this));
                        }
                    }
                });
                var i = index.find('.active').index();

                var vis_above = (num_visible - num_visible % 2) / 2;
                var vis_below = (num_visible + num_visible % 2) / 2 - 1;

                var loaded_below = index.children().length - (i + 1);
                var offset = i - vis_above;
                if (vis_below > loaded_below) {
                    offset = offset - (vis_below - loaded_below);
                }
                index.animate({
                    marginTop: -1 * (offset * 50),
                }, 250);

                var end = false;

                MyelnNotebooks.index_loading = false;

            },
            error: function() {
                MyelnNotebooks.index_loading = false;
            }
        });
    }
}

$(window).resize(function(event) {
    $('main').trigger('scroll');
});

var checkLoading = function(t) {
    return new Promise(function(resolve) {
        var interval = setInterval(function(){
            if (!MyelnNotebooks.loading) {
               resolve();
               clearInterval(interval);
            }
        }, t);
    });
}

function scrollIndex(pk) {
    var el = $('#entry-'+pk);
    if (!el.length) {
        var entries = $('.notebook-entry');
        var elem = entries.first();
        MyelnNotebooks.loading = true;
        loadPage(elem, 'prev', false);
        checkLoading(100).then(function(){
            scrollIndex(pk);
        });
    } else {
        $('#entry-' + pk)[0].scrollIntoView({alignToTop: false, behavior: 'smooth'});
    }
}

function resizeIndex() {
    var mainHeight = $('main').innerHeight();
    var margins = mainHeight % 50;
    if (margins < 40) {
        margins = margins + 50;
    }
    var index_height = mainHeight - margins;
    $('#notebook-index').height(index_height + 1);
    $('#notebook-index').css('margin-bottom', margins/2);
    $('#notebook-index').css('margin-top', margins/2 -1);
    return index_height;
}

MyelnNotebooks.lastViewTop =0;
$('main').on('scroll', function(event) {
    var viewTop = $('main').scrollTop();

    $('.notebook-entry').each(function() {
       var elTop = $(this).offset().top;
       var elBot = elTop + $(this).innerHeight();
       var mainTop = $('main').offset().top;
       var mainBot = mainTop + $('main').height();
       if (elBot > mainTop && elTop < mainBot) {
           $(this).addClass('inview');
           $('#index-'+$(this).data('entry-pk')).addClass('inview');
       } else {
           $(this).removeClass('inview');
           $('#index-'+$(this).data('entry-pk')).removeClass('inview');
       }
    });

    var index_height = resizeIndex();
    var active = $('.notebook-entry.inview').first();
    if (active.data('entry-pk') !== MyelnNotebooks.current_entry && !MyelnNotebooks.index_loading) {
        MyelnNotebooks.current_entry = active.data('entry-pk');
        loadIndex(active, index_height);
    }

    if (!MyelnNotebooks.loading) {
        var entries = $('.notebook-entry');
        if (entries.length == 0) {
            return;
        }

        if (viewTop > MyelnNotebooks.lastViewTop ) {
           var elem = entries.last();
           var hidden = elem.offset().top + elem.height()  - viewTop - $(window).height();
           if ((hidden > 0)&&(hidden < 200)) {
               MyelnNotebooks.loading = true;
               loadPage(elem, 'next');
           }

        } else if (viewTop < MyelnNotebooks.lastViewTop ) {
            var elem = entries.first();
            var hidden = elem.offset().top - viewTop;
           if ((hidden > 0)&&(hidden < 200)) {
               MyelnNotebooks.loading = true;
               loadPage(elem, 'prev');
           }
        }
    }
    MyelnNotebooks.lastViewTop = viewTop;
});


function initEntries(selector) {
    $(selector).each(function(){
        // Math Katex
        renderMathInElement(this);

        //tooltips
        $(this).find('[title]').tooltip();

        //syntax highlighting
/*        $(this).find('pre code').each(function(i, block) {
            hljs.highlightBlock(block);
        });*/

        //Annotations
        markAnnotations(this);
        $(this).find('a.plot-tab[data-toggle="tab"]').on('shown.bs.tab', function(e){
            plotData(e.target);
        });
    });
    $('main').trigger('scroll');
}

function draw_xy_chart() {

    function chart(selection) {
        selection.each(function (datasets) {
            var xoffset = 0;
            if (xlabel) {
                var bmargin = 50;
            } else {
                var bmargin = 20;
            }
            var margin = {top: 20, right: width * 0.1, bottom: bmargin, left: width * 0.1},
                innerwidth = width - margin.left - margin.right,
                innerheight = height - margin.top - margin.bottom;

            var svg = d3.select(this)
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var color_scale = d3.scaleOrdinal(d3.schemeCategory10);
            var y1data = [], y2data = [];
            var y1datasets = [], y2datasets = [];

            if (scatter === 'bar') {
                var color = datasets['color'];
                var xmin = d3.min(datasets.data);
                var xmax = d3.max(datasets.data);
                switch (xscale) {
                    case 'time':
                        var x_scale = d3.scaleTime()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'linear':
                        var x_scale = d3.scaleLinear()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                }
                var bins = d3.histogram()
                    .value(function (d) {
                        return d;
                    })
                    .domain([d3.min(datasets.data), d3.max(datasets.data)])
                    .thresholds(x_scale.ticks(binning))(datasets['data']);
                var y1_scale = d3.scaleLinear()
                    .domain([0, d3.max(bins, function (d) {
                        return d.length;
                    })])
                    .range([innerheight, 0]);
            } else {
                var xmin = d3.min(datasets, function (d) { return d3.min(d.x);});
                var xmax = d3.max(datasets, function (d) { return d3.max(d.x);});
                switch (xscale) {
                    case 'inv-square':

                        var x_scale = d3.scalePow().exponent(-2)
                            .range([0, innerwidth])
                            .domain([xmax, xmin]);
                        break;
                    case 'pow':
                        var x_scale = d3.scalePow()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'log':
                        var x_scale = d3.scaleLog()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'identity':
                        var x_scale = d3.scaleIdentity()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'time':
                        var x_scale = d3.scaleTime()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'linear':
                        var x_scale = d3.scaleLinear()
                            .range([0, innerwidth])
                            .domain([xmin, xmax]);
                        break;
                    case 'inverse':
                        var x_scale = d3.scaleLinear()
                            .range([0, innerwidth])
                            .domain([xmax, xmin]);
                }

                switch(interpolation) {
                    case 'cardinal':
                        var fit = d3.curveCardinal;
                        break;
                    case 'step':
                        var fit = d3.curveStep;
                        break;
                    case 'step-after':
                        var fit = d3.curveStepAfter;
                        break;
                    case 'step-before':
                        var fit = d3.curveStepBefore;
                        break;
                    case 'basis':
                        var fit = d3.curveBasis;
                        break;
                    case 'linear':
                        var fit = d3.curveLinear;
                }

                for (var p = 0; p < datasets.length; p++) {
                    datasets[p]['color'] = color_scale(p);
                    if ((datasets[p]['y1'])) {
                        y1data = y1data.concat(datasets[p]['y1']);
                        y1datasets.push(datasets[p]);
                    }
                    if ((datasets[p]['y2'])) {
                        y2data = y2data.concat(datasets[p]['y2']);
                        y2datasets.push(datasets[p]);
                    }
                }

                var y1_scale = d3.scaleLinear()
                    .range([innerheight - xoffset, 0])
                    .domain([d3.min(y1data), d3.max(y1data)]);

                var y2_scale = d3.scaleLinear()
                    .range([innerheight - xoffset, 0])
                    .domain([d3.min(y2data), d3.max(y2data)]);
            }

            var x_axis = d3.axisBottom()
                .scale(x_scale)
                .tickSize(-innerheight);
            if (xscale === 'inv-square') {
                var ticks = inv_sqrt(Array.cleanspace(Math.pow(xmax, -2), Math.pow(xmin, -2), 8));
                x_axis.tickValues(ticks).tickFormat(d3.format(".3"));
            } else if (xscale === 'time' && timeformat) {
                x_axis.ticks(7).tickFormat(d3.timeFormat(timeformat));
            }

            var y1_axis = d3.axisLeft()
                .scale(y1_scale)
                .tickSize(-innerwidth);

            var y2_axis = d3.axisRight()
                .scale(y2_scale);


            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + (innerheight) + ")")
                .call(x_axis);
            svg.append("text")
                .attr("transform", "translate(" + (innerwidth / 2) + "," + (height - margin.bottom / 2) + ")")
                .style("text-anchor", "middle")
                .text(xlabel);

            svg.append("g")
                .attr("class", "y axis")
                .call(y1_axis)
                .append("text")
                .attr("transform", "translate(0," + innerheight / 2 + "), rotate(-90)")
                .attr("y", 6)
                .attr("dy", "-3.5em")
                .style("text-anchor", "middle")
                .attr("fill", function (_, i) {
                    if (y1datasets.length > 1 || !(y1datasets.length)) {
                        return "#000000";
                    }
                    return y1datasets.length && y1datasets[0]['color'];
                })
                .text(y1label);

            if (scatter === 'bar') {
                var bar = svg.selectAll(".bar")
                    .data(bins)
                    .enter().append("g")
                    .attr("class", "bar")
                    .attr("fill", color)
                    .attr("transform", function(d) { return "translate(" + x_scale(d.x0) + "," + y1_scale(d.length) + ")"; });

                bar.append("rect")
                    .attr("x", 1)
                    .attr("title", function(d) { if (xscale === 'time' && timeformat) {
                        return d3.timeFormat(timeformat)(d.x0) + '-' + d3.timeFormat(timeformat)(d.x1) + ': ' + d.length + 'entries';
                    } else {
                        return d.x0 + '-' + d.x1 + ': ' + d.length + ' entries';
                    } })
                    .attr("width", x_scale(bins[0].x1) - (Math.max(0, x_scale(bins[0].x0) - 1)))
                    .attr("height", function(d) { return innerheight - y1_scale(d.length); });

            } else {

                var y1_draw_line = [], y2_draw_line = [];

                for (var p = 0; p < datasets.length; p++) {
                    if (datasets[p]['y1']) {
                        y1_draw_line.push(d3.line()
                            .curve(fit)
                            .x(function (d) {
                                return x_scale(d[0]);
                            })
                            .y(function (d) {
                                return y1_scale(d[1]);
                            }));
                    } else if (datasets[p]['y2']) {
                        y2_draw_line.push(d3.line()
                            .curve(fit)
                            .x(function (d) {
                                return x_scale(d[0]);
                            })
                            .y(function (d) {
                                return y2_scale(d[1]);
                            }));
                    }
                }

                if (y2data.length) {
                    svg.append("g")
                        .attr("class", "y axis")
                        .attr("transform", "translate(" + innerwidth + ", 0)")
                        .call(y2_axis)
                        .append("text")
                        .attr("transform", "translate(0," + innerheight / 2 + "), rotate(-90)")
                        .attr("y", 55)
                        .attr("dy", 0)
                        .style("text-anchor", "middle")
                        .attr("fill", function (_, i) {
                            if (y2datasets.length > 1) {
                                return "#000000";
                            }
                            return y2datasets[0]['color'];
                        })
                        .text(y2label);
                }

                var y1_data_lines = svg.selectAll(".d3_xy1_chart_line")
                    .data(y1datasets.map(function (d) {
                        return d3.zip(d.x, d.y1);
                    }))
                    .enter().append("g")
                    .attr("class", "d3_xy1_chart_line");
                var y2_data_lines = svg.selectAll(".d3_xy2_chart_line")
                    .data(y2datasets.map(function (d) {
                        return d3.zip(d.x, d.y2);
                    }))
                    .enter().append("g")
                    .attr("class", "d3_xy2_chart_line");

                for (var p = 0; p < y1_draw_line.length; p++) {
                    if (scatter === 'line') {
                        y1_data_lines.append("path")
                            .attr("class", "line")
                            .attr("d", function (d) {
                                return y1_draw_line[p](d);
                            })
                            .attr("data-legend", function (_, l) {
                                return y1datasets[l]['label'] || null;
                            })
                            .attr("stroke", function (_, l) {
                                return y1datasets[l]['color'];
                            })
                            .attr("fill", "none");
                    } else {
                        for (k = 0; k < y1datasets.length; k++) {
                            var newdata = y1datasets[k]['x'].map(function (e, j) {
                                return [e, y1datasets[k]['y1'][j]];
                            });
                            var data_points = svg.selectAll("dot")
                                .data(newdata)
                                .enter().append("circle")
                                .attr("r", 2)
                                .attr("cx", function (d) {
                                    return x_scale(d[0]);
                                })
                                .attr("cy", function (d) {
                                    return y1_scale(d[1]);
                                })
                                .attr("fill", function (_, l) {
                                    return y1datasets[k]['color'];
                                });
                        }
                    }
                }

                for (var p = 0; p < y2_draw_line.length; p++) {
                    if (scatter === 'line') {
                        y2_data_lines.append("path")
                            .attr("class", "line")
                            .attr("d", function (d) {
                                return y2_draw_line[p](d);
                            })
                            .attr("data-legend", function (_, l) {
                                return y2datasets[l]['label'] || null;
                            })
                            .attr("stroke", function (_, l) {
                                return y2datasets[l]['color'];
                            })
                            .attr("fill", "none");
                    } else {
                        for (k = 0; k < y2datasets.length; k++) {
                            var newdata = y2datasets[k]['x'].map(function (e, j) {
                                return [e, y2datasets[k]['y2'][j]];
                            });
                            var data_points = svg.selectAll("dot")
                                .data(newdata)
                                .enter().append("circle")
                                .attr("r", 2)
                                .attr("cx", function (d) {
                                    return x_scale(d[0]);
                                })
                                .attr("cy", function (d) {
                                    return y2_scale(d[1]);
                                })
                                .attr("fill", function (_, l) {
                                    return y2datasets[k]['color'];
                                });
                        }
                    }
                }



                legend = svg.append("g")
                    .attr("class", "legend")
                    .attr("transform", "translate(50,30)")
                    .call(d3.legend);


                /* Interactive stuff */
                var mouseG = svg.append("g")
                    .attr("class", "mouse-over-effects");

                mouseG.append("path") // this is the black vertical line to follow mouse
                    .attr("class", "mouse-line")
                    .style("stroke", "#333")
                    .style("stroke-width", "0.5px")
                    .style("opacity", "0");

                var lines = $(this).find('.line');

                if (y2datasets) {
                    var dualdatasets = [];
                    for (var p = 0; p < y1datasets.length; p++) {
                        dualdatasets.push({'x': y1datasets[p]['x'], 'y1': y1datasets[p]['y1']});
                    }
                    for (var p = 0; p < y2datasets.length; p++) {
                        dualdatasets.push({'x': y2datasets[p]['x'], 'y1': y2datasets[p]['y2'], 'scale': y2_scale});
                    }
                    var mousePerLine = mouseG.selectAll('.mouse-per-line')
                        .data(dualdatasets)
                        .enter()
                        .append("g")
                        .attr("class", "mouse-per-line");
                } else {
                    var mousePerLine = mouseG.selectAll('.mouse-per-line')
                        .data(datasets)
                        .enter()
                        .append("g")
                        .attr("class", "mouse-per-line");
                }

                mousePerLine.append("circle")
                    .attr("r", 2)
                    .style("fill", "none")
                    .style("stroke-width", "4px")
                    .style("opacity", "0");

                mousePerLine.append("text")
                    .attr("transform", "translate(10,3)");

                var mouseX = svg.append("text")
                    .attr("transform", "translate(" + (innerwidth - 3) + ", " + (innerheight - 3) + ")")
                    .style("text-anchor", "end")
                    .style("opacity", "0");

                mouseG.append('rect')
                    .attr('width', innerwidth)
                    .attr('height', innerheight)
                    .attr('fill', 'none')
                    .attr('pointer-events', 'all')
                    .on('mouseout', function () {
                        svg.select(".mouse-line").style("opacity", "0");
                        svg.selectAll(".mouse-per-line circle").style("opacity", "0");
                        svg.selectAll(".mouse-per-line text").style("opacity", "0");
                        mouseX.style("opacity", "1");
                    })
                    .on('mouseover', function (e) {
                        svg.select(".mouse-line").style("opacity", "1");
                        svg.selectAll(".mouse-per-line circle").style("opacity", "1");
                        svg.selectAll(".mouse-per-line text").style("opacity", "1");
                        mouseX.style("opacity", "1");

                    })
                    .on('mousemove', function () {
                        var mouse = d3.mouse(this);
                        svg.select(".mouse-line")
                            .attr("d", function () {
                                var d = "M" + mouse[0] + "," + innerheight;
                                d += " " + mouse[0] + "," + 0;
                                return d;
                            });
                        svg.selectAll(".mouse-per-line")
                            .style("stroke", function (d, n) {
                                return color_scale(n);
                            })
                            .attr("transform", function (d, n) {
                                var xPos = x_scale.invert(mouse[0]);
                                mouseX.text("X = " + xPos.toFixed(2));
                                var closest = d['x'].reduce(function (prev, curr) {
                                    return (Math.abs(curr - xPos) < Math.abs(prev - xPos) ? curr : prev);
                                });
                                var i = d['x'].indexOf(closest);

                                var scale = d['scale'] || y1_scale;
                                var pos = scale(d['y1'][i]);
                                d3.select(this).select('text')
                                    .style("stroke", "none")
                                    .text(scale.invert(pos).toFixed(2));
                                return "translate(" + x_scale(closest) + "," + pos + ")";
                            });
                    });
                /* End of interactive stuff */
            }
        });

    }

    chart.width = function (value) {
        if (!arguments.length) return width;
        width = value;
        return chart;
    };

    chart.height = function (value) {
        if (!arguments.length) return height;
        height = value;
        return chart;
    };

    chart.xlabel = function (value) {
        if (!arguments.length) return xlabel || '';
        xlabel = value;
        return chart;
    };

    chart.y1label = function (value) {
        if (!arguments.length) return y1label;
        y1label = value;
        return chart;
    };

    chart.y2label = function (value) {
        if (!arguments.length) return y2label;
        y2label = value;
        return chart;
    };

    chart.xscale = function (value) {
        if (!arguments.length) return xscale;
        xscale = value;
        return chart;
    };
    chart.scatter = function (value) {
        if (!arguments.length) return scatter;
        scatter = value;
        return chart;
    };
    chart.interpolation = function (value) {
        if (!arguments.length) return interpolation;
        interpolation = value;
        return chart;
    };
    chart.binning = function (value) {
        if (!arguments.length) return binning;
        binning = value;
        return chart;
    };
    chart.timeformat = function (value) {
        if (!arguments.length) return timeformat;
        timeformat = value;
        return chart;
    };

    return chart;
}

function drawStackChart(data, label, canvasStackChart, colorStackChart, xStackChart, yStackChart, heightStackChart) {

    colorStackChart.domain(d3.keys(data[0]).filter(function (key) { return key !== label && key !== 'color'; }));

    data.forEach(function (d) {
        var y0 = 0;
        d.ages = colorStackChart.domain().map(function (name) { return { name: name, y0: y0, y1: y0 += +d[name], color: d['color'] || null, label: d[label] }; });
        d.total = d.ages[d.ages.length - 1].y1;
    });

    xStackChart.domain(data.map(function (d) { return d[label]; }));
    yStackChart.domain([0, d3.max(data, function (d) { return d.total; })]);

    canvasStackChart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + heightStackChart + ")")
        .call(d3.axisBottom(xStackChart))
        .selectAll("text")
        .attr("y", 10)
        .attr("x", -10)
        .attr("dy", ".35em")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    var state = canvasStackChart.selectAll("."+label+"")
        .data(data)
        .enter().append("g")
        .attr("class", "g")
        .attr("transform", function (d) { return "translate(" + xStackChart(d[label]) + ",0)"; });

    var yaxis = canvasStackChart.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(yStackChart));

    var active_link = "0";
    var legendClassArray = [];
    var legend = canvasStackChart.selectAll(".legend")
        .data(colorStackChart.domain().slice().reverse())
        .enter().append("g")
        .attr("class", function (d) {
            legendClassArray.push(d.replace(/\s/g, '')); //remove spaces
            return "legend";
        })
        .attr("transform", function(d, i) { return "translate(20," + i * 20 + ")"; });

    //reverse order to match order in which bars are stacked
    legendClassArray = legendClassArray.reverse();

    state.selectAll("rect")
        .data(function (d) { return d.ages; })
        .enter().append("rect")
        .attr("width", xStackChart.bandwidth())
        .attr("class", function(i, d) { return 'class' + legendClassArray[d]; })
        .attr("title", function(d, i) { return legendClassArray[i] + ' (' + d.label + '): ' + (d.y1 - d.y0);})
        .attr("y", function (d) { return yStackChart(d.y1); })
        .attr("height", function (d) { return yStackChart(d.y0) - yStackChart(d.y1); })
        .style("fill", function (d) { return d.color && d.color || colorStackChart(d.name); })
        .style("opacity", function (d, i) { return d.color && 1 - ((0.75/legendClassArray.length) * i) || 1});


    if (legendClassArray.length > 1) {
        legend.append("circle")
            .attr("cy", 9)
            .attr("r", 9)
            .style("fill", colorStackChart)
            .attr("id", function (d, i) {
                return "id" + d.replace(/\s/g, '');
            })
            .on("mouseover", function () {
                if (active_link === "0") d3.select(this).style("cursor", "pointer");
                else {
                    if (active_link.split("class").pop() === this.id.split("id").pop()) {
                        d3.select(this).style("cursor", "pointer");
                    } else d3.select(this).style("cursor", "auto");
                }
            })
            .on("click", function (d) {
                var active_id = '#id' + active_link;
                d3.select(active_id).style("stroke", "none");
                if (active_link !== this.id.split("id").pop()) {
                    if (active_link !== "0") {
                        restorePlot($(active_id)[0], duration = 1, delay = 1);
                    }
                    d3.select(this)
                        .style("stroke", "black")
                        .style("stroke-width", 2);

                    active_link = this.id.split("id").pop();
                    plotSingle(this);
                } else {
                    restorePlot($(active_id)[0], duration=500, delay=100);
                    active_link = "0";
                }
            });

        legend.append("text")
            .attr("x", 24)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "start")
            .text(function (d) {
                return d;
            });
    }

    function restorePlot(d, duration, delay) {
        duration = duration || 500;
        delay = delay || 100;
        class_keep = d.id.split("id").pop();
        idx = legendClassArray.indexOf(class_keep);

        $.each(state.selectAll("rect"), function (i, e) {
            //get height and y posn of base bar and selected bar
            $.each(e, function(j, r) {
                if (r[idx]) {
                    d3.select(r[idx])
                        .transition()
                        .ease(d3.easeBounce)
                        .duration(duration)
                        .delay(delay)
                        .attr("y", y_orig[j])
                        .attr("height", h_orig[j]);
                }
            });
        });

        //restore opacity of erased bars
        for (i = 0; i < legendClassArray.length; i++) {
          if (legendClassArray[i] != class_keep) {
            state.selectAll(".class" + legendClassArray[i])
              .transition()
              .duration(duration)
              .delay(delay)
              .style('display', 'block');
          }
        }
        yaxis.remove();
        yaxis = canvasStackChart.append("g")
            .attr("class", "y axis")
            .call(d3.axisLeft(yStackChart));

    }

    function plotSingle(d) {
        class_keep = d.id.split("id").pop();
        idx = legendClassArray.indexOf(class_keep);
        key_keep = class_keep;
        $.each(data[0], function(k) {
            if (k.replace(/\s/g, '') === class_keep) {
                key_keep = k;
                return false;
            }
        });
        ySingleChart = d3.scaleLinear().range([heightStackChart, 0]).domain([0, d3.max(data, function (d) { return d[key_keep]; })]);

        yaxis.remove();
        yaxis = canvasStackChart.append("g")
            .attr("class", "y axis")
            .call(d3.axisLeft(ySingleChart));

        for (i = 0; i < legendClassArray.length; i++) {
            if (legendClassArray[i] != class_keep) {
                state.selectAll(".class" + legendClassArray[i])
                    .transition()
                    .duration(500)
                    .style("display", "none");
            }
        }

        y_orig = [], h_orig = [];
        $.each(state.selectAll("rect"), function (i, d) {
            //get height and y posn of base bar and selected bar

            $.each(d, function(j, r) {
                if (r[idx]) {
                    h_keep = d3.select(r[idx]).attr("height");
                    y_keep = d3.select(r[idx]).attr("y");
                    y_orig.push(y_keep);
                    h_orig.push(h_keep);

                    h_base = d3.select(r[0]).attr("height");
                    y_base = d3.select(r[0]).attr("y");

                    h_shift = h_keep - h_base;
                    y_new = y_base - h_shift;

                    d3.select(r[idx])
                        .transition()
                        .ease(d3.easeBounce)
                        .duration(500)
                        .delay(100)
                        .attr("y", function (d) { return heightStackChart - (ySingleChart(d.y0) - ySingleChart(d.y1)); })
                        .attr("height", function (d) { return ySingleChart(d.y0) - ySingleChart(d.y1);})
                        .call(yStackChart);
                }
            });

        });

    }
}


function plotData(element) {
    var entry = $(element).closest('.notebook-entry');
    var pk = entry.data('entry-pk');

    var info = JSON.parse(entry.find('script#plot-data-' + pk).text());

    //remove the existing figure, if there is one
    var fig = $("#plot-" + pk + ' figure');
    if (fig.length) {
        fig.remove();
    }
    $("#plot-" + pk).append("<figure id='figure-" + pk + "'></figure>");
    var width = $('#figure-' + pk).width();
    var data = [];
    var xlabel = entry.find('.x-axis').val() || null;
    var y1label = entry.find('.y1-axis').val();
    var y2label = entry.find('.y2-axis').val();
    var xindex = info['headers'].indexOf(xlabel);
    var y1index = info['headers'].indexOf(y1label);
    var y2index = y2label && info['headers'].indexOf(y2label) || false;
    var xscale = 'linear';
    var interpolation = 'linear';
    var binning = 50;
    var timeformat =  null;

    //check if this should be a scatter plot or a bar graph
    var barchart = true;
    $.each(info['data'][xindex], function (i, val) {
        if (parseFloat(val)) {
            barchart = false;
        }
    });

    if (barchart) {
        $.each(info['data'][xindex], function (i, val) {
            var point = {};
            var addPoint = false;
            if (parseFloat(info['data'][y1index][i])) {
                point[xlabel] = val;
                point[y1label] = parseFloat(info['data'][y1index][i]);
                addPoint = true;
            }
            if (y2label && parseFloat(info['data'][y2index][i])) {
                point[y2label] = parseFloat(info['data'][y2index][i]);
            }
            if (addPoint) {
                data.push(point);
            }
        });

        //Draw Stack Chart
        var margin = { top: 20, right: 20, bottom: 50, left: 40 };

        var x = d3.scaleBand().range([0, width]).padding(0.1);
        var y = d3.scaleLinear().range([width/2, 0]);
        var colors = d3.scaleOrdinal(["#883A6A", "#C27844", "#551863", "#CBEFB6", "#5BC0DE"]);

        var canvas = d3.select('#figure-' + pk).append("svg").attr('id', 'plot-' + pk)
            .attr("width", width + margin.left + margin.right)
            .attr("height", width/2 + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        drawStackChart(data, xlabel, canvas, colors, x, y, width/2);
    } else {
        if (y1label) {
            var x = [], y = [];
            $.each(info['data'][xindex], function (i, val) {
                if (parseFloat(val) && parseFloat(info['data'][y1index][i])) {
                    x.push(parseFloat(val));
                    y.push(parseFloat(info['data'][y1index][i]));
                }
            });
            data.push({'label': y1label, 'x': x, 'y1': y});
        }
        if (y2label) {
            var x = [], y = [];
            $.each(info['data'][xindex], function (i, val) {
                if (parseFloat(val) && parseFloat(info['data'][y2index][i])) {
                    x.push(parseFloat(val));
                    y.push(parseFloat(info['data'][y2index][i]));
                }
            });
            data.push({'label': y1label, 'x': x, 'y2': y});
        }

        var xy_chart = draw_xy_chart()
            .width(width)
            .height(width / 2)
            .xlabel(xlabel)
            .y1label(y1label)
            .y2label(y2label)
            .xscale(xscale)
            .binning(binning)
            .timeformat(timeformat)
            .interpolation(interpolation)
            .scatter('scatter');
        var svg = d3.select('#figure-' + pk).append("svg").attr('id', 'plot-' + pk)
            .datum(data)
            .call(xy_chart);
    }
}