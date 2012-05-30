var logged_in = false;
var base_url = '';

var item_types = [];
var item_ids = [];
var comment_ids = [];
var editable_comments = [];
var page_id = '';
loggingPane = null;
var unthrob_text = new Object;
var unthrob_element = new Object;
var block_autosave = false;
var dialog_box = null;
var current_field_id = null;
var newly_uploaded_files = [];
var current_subdir = '';
var current_upload_subdir = '';

function blog_my_onload() {
  connect($('title_itself'), 'onclick', this, 'go_home');
  
  if ($('login_link')) { // little link style
    connect($('login_link'), 'onclick', this, 'login_click');
  } else {              // magic shift-click style
    connect($('title_box'), 'onclick', this, 'login_click');
  }
  
  update_login_box();
  update_edit_links();
  upate_loggingPane();
  create_messages();
  
  dialog_box = new DialogBox({'id':'dialog_box','element_id':'blog_my_dialog_box','images_url':base_url+'/'});
  new Draggable('blog_my_dialog_box',{'handle':this.dialog_box.element.id+'_header','starteffect':null,'endeffect':null});
}

function go_home(evt) {
  location.href = base_url+'/';
}

function login_click(evt) {
  if (evt.modifier().shift || $('login_link')) {
    disconnectAll($('login_name'));
    disconnectAll($('login_pwd'));
    if (computedStyle($('login_box'), 'display') == 'none') {
      showElement($('login_box'));
      connect($('login_name'), 'onkeyup', this, 'login_keypress');
      connect($('login_pwd'), 'onkeyup', this, 'login_keypress');
    } else {
      hideElement($('login_box'));
    }
  }
}

function draw_messages(messages) {
  if (typeof(messages) == 'string')
    messages = [messages];

  results = '';

  for (message in messages) {
    message = message.replace(/\[E\](.+?)/g, function($str, $1) { return '<div class="error_message"/><div class="icon"'+$1+'</div></div>';});
    message = message.replace(/\[I\](.+?)/g, function($str, $1) { return '<div class="info_message"/><div class="icon"'+$1+'</div></div>';});
    message = message.replace(/\[W\](.+?)/g, function($str, $1) { return '<div class="warning_message"/><div class="icon"'+$1+'</div></div>';});
    results += 'message';
  }
  return results;
}

function create_messages() {
  temp = createDOM('div', {'id':'messages'});
  temp.className = 'messages';
  temp.innerHTML = '';
  $('title_box').appendChild(temp, $('site_menu'));
}


function show_messages(messages) {
  if (!messages || messages == null) return;
  $('messages').innerHTML = draw_messages(messages);
  showElement($('messages'));
  position_messages();
}

function position_messages() {
  var el = $('messages');
  var eldim = getElementDimensions(el);
  var screendim = getViewportDimensions();
  var x = Math.floor((screendim.w - eldim.w) /2);
  setElementPosition(el, {'x':x});
}


function login_keypress(evt) {
  if (evt.key().code == 13)
    login_submit();
}

function login_submit() {
  var login_name = $('login_name').value;
  var login_password = $('login_pwd').value;
  
  var url = base_url+'/login/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  var data = queryString(['login_name','login_password'],[login_name,login_password]);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true')
        logged_in = true;
      update_login_box();
      update_edit_links();
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    new_window_show(err.req.responseText);
  });
}

function logout_submit() {
  var url = base_url+'/logout/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  var d = sendXMLHttpRequest(req);
  d.addCallback(function(rsp) {
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true')
        logged_in = false;
      update_login_box();
      update_edit_links();
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    new_window_show(err.req.responseText);
  });
}

function load_item(item_id) {
  var url = base_url+'/js/get_item/'+item_id;
  var req = getXMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  //new_window_show(req.responseText);
  var results = eval('(' + req.responseText + ')');
  return results;
}

function load_page(pname) {
  var url = base_url+'/js/get_page/'+pname;
  var req = getXMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  var results = eval('(' + req.responseText + ')');
  return results;
}

function load_comment(item_id, comment_id) {
  var url = base_url+'/js/get_item/'+item_id+'/comment/'+comment_id;
  var req = getXMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  //new_window_show(req.responseText);
  var results = eval('(' + req.responseText + ')');
  return results;
}




// autosave modes:
// 0 (none)
// 1 (use autosaved version)
// 2 (use original version)

function edit_item(item_id, item, evt) {
  block_autosave = false;
  var edit_item;
  
  if (item) {
    edit_item = item;
  }
  else {
    edit_item = load_item(item_id);
    if (edit_item['autosaved']) {
      autosaved_item = edit_item['autosaved'];
      var edit_text = '';
      edit_text += '<div id="edit_item" class="item">';
      edit_text += '<div class="header headline">Editing</div>';
      edit_text += '<div id="use_autosave_box" class="header button">Edit autosaved version</div>';
      edit_text += '<div id="toss_autosave_box" class="header button">Toss autosaved version, edit original version</div>';
 

      edit_text += '<div class="border">';
      edit_text += '<br style="clear:left;"/>';
      edit_text += '<br style="clear:left;"/>';
      edit_text += 'This '+autosaved_item.type+' has an autosaved version (below).  Use it?';
      edit_text += '</div></div>';
      
      $('edit_area').innerHTML = edit_text;
      hideElement($('main_area'));
      showElement($('edit_area'));
      
      connect($('use_autosave_box'), 'onclick', partial(self.edit_item, item_id, edit_item['autosaved']));
      connect($('toss_autosave_box'), 'onclick', partial(self.edit_item, item_id, edit_item['item']));
      return;
    } else {
      edit_item = edit_item['item'];
    }
  }
  
  
  var edit_text = '';
  edit_text += '<div id="edit_item" class="item">';
  edit_text += '<div class="header headline">Editing</div>';
  edit_text += '<div id="preview_edit_box" class="header button edit_preview">Preview</div>';
  edit_text += '<div id="save_edit_box" class="header button edit_save">Save</div>';
  
  edit_text += '<div id="delete_edit_box" class="header button edit_delete">Delete</div>';
  edit_text += '<div id="cancel_edit_box" class="header button edit_cancel">Cancel Edit</div>';

  edit_text += '<div class="border">';
  edit_text += '<br style="clear:left;"/>';
  
  for (item_field_index in item_fields[edit_item.type]) {
    item_field = item_fields[edit_item.type][item_field_index];
    field_value = edit_item[item_field];
    field_id = 'edit_field_'+item_field;
    
    var unescaped_field_value = unescape(field_value);
    var hasnewlines = (unescaped_field_value.match(/\n/)) ? true : false;

    unescaped_field_value = unescaped_field_value.replace(/&/g,'&amp;');
    unescaped_field_value = unescaped_field_value.replace(/</g,'&lt;');
    unescaped_field_value = unescaped_field_value.replace(/>/g,'&gt;');

    edit_text += '<div class="edit_field">';
    if (hasnewlines || edit_item[item_field].length > 100)
      edit_text += '<label for="'+field_id+'">'+item_field+':</label><textarea id="'+field_id+'" style="height:20em;">'+unescaped_field_value+'</textarea>';
    else {
      var quoted_field_value = field_value.replace(/"/g,'&quot;');
      edit_text += '<label for="'+field_id+'">'+item_field+':</label><input id="'+field_id+'" type="text" value="'+quoted_field_value+'"/>';
    }
      
    edit_text += '<img id="'+field_id+'_grow" src="/larger.gif"/>';
    edit_text += '<img id="'+field_id+'_shrink" src="/smaller.gif"/>';
    edit_text += '<br/></div>';
  }
  
  // preserve timestamp
  edit_text += '<div class="edit_field">';
  edit_text += '<input type="checkbox" id="preserve_timestamp"/><label for="preserve_timestamp" style="width:auto;">Preserve timestamp</label>';
  edit_text += '<br/></div>';
  
  // disable comments
  var disable_comments = (edit_item.disable_comments) ? ' checked':'';
  edit_text += '<div class="edit_field">';
  edit_text += '<input type="checkbox" id="disable_comments"'+disable_comments+'/><label for="disable_comments" style="width:auto;">Disable comments</label>';
  edit_text += '<br/></div>';
  
  // draft
  var draft = (edit_item.draft) ? ' checked':'';
  edit_text += '<div class="edit_field">';
  edit_text += '<input type="checkbox" id="draft"'+draft+'/><label for="draft" style="width:auto;">Draft</label>';
  edit_text += '<br/></div>';

  
  edit_text += '<br style="clear:left;"/>';
  edit_text += '<div id="files_dialog_box" class="header button files_dialog">Files</div>';
  edit_text += '</div></div>';
  
  $('edit_area').innerHTML = edit_text;
  
  hideElement($('main_area'));
  showElement($('edit_area'));
  connect($('preview_edit_box'), 'onclick', partial(self.preview_edit_item, edit_item.type));
  connect($('save_edit_box'), 'onclick', partial(self.save_edit_item, edit_item.type, item_id));
  connect($('delete_edit_box'), 'onclick', partial(self.delete_item, item_id));
  connect($('cancel_edit_box'), 'onclick', cancel_edit_item);
  connect($('files_dialog_box'), 'onclick', files_dialog);
  
  setTimeout('autosave(\''+edit_item.type+'\',\''+item_id+'\')',30000);
  
  
  for (item_field_index in item_fields[edit_item.type]) {
    item_field = item_fields[edit_item.type][item_field_index];
    field_id = 'edit_field_'+item_field;
    connect($(field_id+'_grow'), 'onclick', partial(self.grow_shrink_field, field_id, true));
    connect($(field_id+'_shrink'), 'onclick', partial(self.grow_shrink_field, field_id, false));
    connect($(field_id), 'onfocus', partial(self.setfieldfocus, field_id));
  }
}

function setfieldfocus(field_id,evt) {
  current_field_id = field_id;
}


function grow_shrink_field(field_id, grow, evt) {
  var size = getElementDimensions(field_id);
  if (grow) {
    if ($(field_id).tagName.toLowerCase() == 'input') {
      var oldvalue = $(field_id).value;
      var newinput = createDOM('textarea', {'id':field_id});
      swapDOM($(field_id),newinput)
      $(field_id).value = oldvalue;
    }
    setElementDimensions(field_id, {'h':size.h + 100});
  }
  else
    setElementDimensions(field_id, {'h':size.h - 100});
}


function add_item(item_type, evt) {
  var edit_text = '';
  edit_text += '<div id="edit_item" class="item">';
  edit_text += '<div class="header headline">Add</div>';
  if (!item_type) {
    for (var item_singular in item_fields) {
      if (item_singular == 'page') continue;
      disconnectAll($('add_'+item_singular));
      edit_text += '<div id="add_'+item_singular+'" class="header button edit_save">';
      edit_text += item_singular;
      edit_text += '</div>';
    }
  } else {
    edit_text += '<div id="preview_edit_box" class="header button edit_preview">Preview</div>';
    edit_text += '<div id="save_edit_box" class="header button edit_save">Save</div>';
  }
  edit_text += '<div id="cancel_edit_box" class="header button edit_cancel">Cancel Add</div>';

  edit_text += '<div class="border">';
  edit_text += '<br style="clear:left;"/>';
  
  if (item_type) {
    edit_text += 'Adding new '+item_type;
    for (item_field_index in item_fields[item_type]) {
      item_field = item_fields[item_type][item_field_index];
      var field_id = 'edit_field_'+item_field;
      edit_text += '<div class="edit_field">';
      if (item_type == 'page' && item_field == 'contents')
        edit_text += '<label for="'+field_id+'">'+item_field+':</label><textarea id="'+field_id+'" style="height:20em;"></textarea>';
      else
        edit_text += '<label for="'+field_id+'">'+item_field+':</label><input id="'+field_id+'" type="text" value=""/>';
      edit_text += '<img id="'+field_id+'_grow" src="/larger.gif"/>';
      edit_text += '<br/></div>';
    }
    
    // disable comments
    var disable_comments = (edit_item.disable_comments) ? ' checked':'';
    edit_text += '<div class="edit_field">';
    edit_text += '<input type="checkbox" id="disable_comments"'+disable_comments+'/><label for="disable_comments" style="width:auto;">Disable comments</label>';
    edit_text += '<br/></div>';
    
    // draft
    var draft = (edit_item.draft) ? ' checked':'';
    edit_text += '<div class="edit_field">';
    edit_text += '<input type="checkbox" id="draft"'+draft+'/><label for="draft" style="width:auto;">Draft</label>';
    edit_text += '<br/></div>';
  }
  

  
  edit_text += '<br style="clear:left;"/>';
  edit_text += '<div id="files_dialog_box" class="header button files_dialog">Files</div>';
  edit_text += '</div></div>';
  
  $('edit_area').innerHTML = edit_text;
  
  if (!item_type)
    for (var item_singular in item_fields) {
      if (item_singular == 'page') continue;
      connect($('add_'+item_singular), 'onclick', partial(self.add_item, item_singular));
    }
    
  if (item_type) {
    for (item_field_index in item_fields[item_type]) {
      item_field = item_fields[item_type][item_field_index];
      var field_id = 'edit_field_'+item_field;
      connect($(field_id+'_grow'), 'onclick', partial(self.grow_shrink_field, field_id, true));
      //connect($(field_id+'_shrink'), 'onclick', partial(self.grow_shrink_field, field_id, false));
      connect($(field_id), 'onfocus', partial(self.setfieldfocus, field_id));
    }
  }
 
  hideElement($('main_area'));
  showElement($('edit_area'));
  connect($('cancel_edit_box'), 'onclick', cancel_edit_item);
  connect($('files_dialog_box'), 'onclick', files_dialog);
  
  if (item_type) {
    connect($('save_edit_box'), 'onclick', partial(self.save_new_item, item_type));
    connect($('preview_edit_box'), 'onclick', partial(self.preview_edit_item, item_type));

  }
}


function cancel_edit_item() {
  try {disconnectAll($('cancel_edit_box'));} catch (e) {}
  try {disconnectAll($('save_edit_box'));} catch (e) {}
  try {disconnectAll($('delete_edit_box'));} catch (e) {}
  try {disconnectAll($('files_dialog_box'));} catch (e) {}
  
  hideElement($('edit_area'));
  showElement($('main_area'));
  $('edit_area').innerHTML = '';
}


function delete_item(item_id, evt) {
  var url = base_url+'/delete_item/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  var field_keys = ['id'];
  var field_values = [item_id];

  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true') {
        go_home();
      }
        
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    new_window_show(err.req.responseText);
  });
}


function save_new_item(item_type, evt) {
  throb($('save_edit_box'),'Saving...');

  var url = base_url+'/add_item/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var field_keys = ['__item_type__'];
  var field_values = [item_type];
  
  if (item_type == 'page') {
    field_keys.push('__id__');
    field_values.push(page_id);
  }
  
  if ($('disable_comments').checked) {
    field_keys.push('__disable_comments__');
    field_values.push('true');
  }
  
  if ($('draft').checked) {
    field_keys.push('__draft__');
    field_values.push('true');
  }

  for (item_field_index in item_fields[item_type]) {
    item_field = item_fields[item_type][item_field_index];
    var field_id = 'edit_field_'+item_field;
    field_keys.push(item_field);
    field_values.push($(field_id).value);
  }
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('save_edit_box'));
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true') {
        if (item_type == 'page')
          location.href = base_url+'/'+jsondata.item_id;
        else
          location.href = base_url+'/view/'+jsondata.item_id;
      }
        
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('save_edit_box'));
    new_window_show(err.req.responseText);
  });
}

function save_edit_item(item_type, item_id, evt) {
  block_autosave = true;
  throb($('save_edit_box'),'Saving...');

  var url = base_url+'/update_item/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var field_keys = ['__id__'];
  var field_values = [];
  
  if (item_type == 'page')
    field_values.push(page_id);
  else
    field_values.push(item_id);
  
  if ($('disable_comments').checked) {
    field_keys.push('__disable_comments__');
    field_values.push('true');
  }
  
  if ($('preserve_timestamp').checked) {
    field_keys.push('__preserve_timestamp__');
    field_values.push('true');
  }
  
  if ($('draft').checked) {
    field_keys.push('__draft__');
    field_values.push('true');
  }
    
  for (item_field_index in item_fields[item_type]) {
    item_field = item_fields[item_type][item_field_index];
    var field_id = 'edit_field_'+item_field;
    field_keys.push(item_field);
    field_values.push($(field_id).value);
  }
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('save_edit_box'));
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true') {
        if (item_type == 'page')
          location.href = base_url+'/'+jsondata.item_id;
        else
          location.href = base_url+'/view/'+jsondata.item_id;
      }
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('save_edit_box'));
    new_window_show(err.req.responseText);
  });
}

function autosave(item_type, item_id) {
  if (block_autosave == true) return;
  throb($('save_edit_box'),'Autosaving...');

  var url = base_url+'/update_item/';
  //var url = base_url+'/autosave_item/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var field_keys = ['__autosave__','__id__'];
  var field_values = [1];
  
  if (item_type == 'page')
    field_values.push(page_id);
  else
    field_values.push(item_id);
    
  for (item_field_index in item_fields[item_type]) {
    item_field = item_fields[item_type][item_field_index];
    var field_id = 'edit_field_'+item_field;
    field_keys.push(item_field);
    field_values.push($(field_id).value);
  }
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('save_edit_box'));
    try {
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('save_edit_box'));
    new_window_show(err.req.responseText);
  });

  setTimeout('autosave(\''+item_type+'\',\''+item_id+'\')',10000);
}



function preview_edit_item(item_type, evt) {
  throb($('preview_edit_box'),'Previewing...');
  
  var url = base_url+'/preview/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var field_keys = ['__item_type__'];
  var field_values = [item_type];
  
  if (item_type == 'page') {
    field_keys.push('__id__');
    field_values.push(page_id);
  }
  
  for (item_field_index in item_fields[item_type]) {
    item_field = item_fields[item_type][item_field_index];
    var field_id = 'edit_field_'+item_field;
    field_keys.push(item_field);
    field_values.push($(field_id).value);
  }
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('preview_edit_box'));
    try {
      preview_window = this.open('', 'preview_window', 'resizable=yes,status=yes,scrollbars=yes,locationbar=yes,location=yes,menubar=yes,toolbar=yes,width=1000,height=1000');
 
      doc = preview_window.document;
      doc.open('text/html');
      doc.write(rsp.responseText);
      doc.close();
      preview_window.focus();
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    new_window_show(err.req.responseText);
  });
}

function add_comment_edit_links(item_id, comment_id) {
  var comment_element_id = 'item_'+item_id+'_comment_'+comment_id;
  var comment_element = $(comment_element_id);
  
  var edit_button = document.createElement('div');
  edit_button.id = 'comment_edit_box_'+comment_id;
  edit_button.className = 'header_button';
  edit_button.innerHTML = 'edit';
  comment_element.insertBefore(edit_button, comment_element.firstChild.nextSibling.nextSibling);
  connect(edit_button, 'onclick', partial(self.edit_comment, item_id, comment_id));
  
  var delete_button = document.createElement('div');
  delete_button.id = 'comment_delete_box_'+comment_id;
  delete_button.className = 'header_button';
  delete_button.innerHTML = 'delete';
  comment_element.insertBefore(delete_button, edit_button.nextSibling.nextSibling);
  connect(delete_button, 'onclick', partial(self.delete_comment, item_id, comment_id));
}


function draw_add_edit_comment(comment_id) {
  var id_text = (comment_id == 'new') ? 'add_new_comment':'edit_comment_'+comment_id;
  var submit_text = (comment_id == 'new') ? 'Add!':'Save!';

  results = '';
  results += '<div class="border add_edit">';
  results += '<div class="edit_field"><label for="'+id_text+'_by">Name:</label><input id="'+id_text+'_by" type="text" value=""/></div>';
  results += '<div class="edit_field"><label for="'+id_text+'_link">Email/Website:</label><input id="'+id_text+'_link" type="text" value=""/></div>';
  results += '<div class="edit_field"><label for="'+id_text+'_text">Comment:</label><textarea rows="6" id="'+id_text+'_text"></textarea></div>';
  results += '<div id="'+id_text+'_submit_button" class="add_comment_button">'+submit_text+'</div>';
  results += '<br style="clear:left;"/>';
  results += '<br style="clear:left;"/>';
  results += '</div>';

  return results;
}



function add_comment(evt) {
  var url = base_url+'/add_comment/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var by = $('add_new_comment_by').value;
  var lnk = $('add_new_comment_link').value;
  var txt = $('add_new_comment_text').value;
  if (!txt.match(/\S/)) {
    alert('Blank comment not added');
    return;
  }
  
  throb($('add_new_comment_submit_button'),'Adding...');
  
  var field_keys = ['item_id','by','link','text','t'];
  var item_id = (page_id == '') ? item_ids[0] : page_id;
  var field_values = [item_id,by,lnk,txt,rightnow];
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    try {
      unthrob($('add_new_comment_submit_button'));

      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true') {
        $('add_new_comment_by').value = '';
        $('add_new_comment_link').value = '';
        $('add_new_comment_text').value = '';

        editable_comments.push(jsondata.new_comment_id);
        comment_ids.push(jsondata.new_comment_id);
        
        var last_comment_element =  $('item_'+item_id+'_comment_'+comment_ids[comment_ids.length-1]);
        
        var new_comment = document.createElement('div');
        new_comment.id = 'temp_'+jsondata.new_comment_id;
        new_comment.innerHTML = jsondata.comment_html;
        
        $('main_area').insertBefore(new_comment,null);
        add_comment_edit_links(item_id,jsondata.new_comment_id);
        new ScrollTo(new_comment.id,{'delay':0,'duration':0});
      }
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('add_new_comment_submit_button'));
    new_window_show(err.req.responseText);
  });
}

function delete_comment(item_id, comment_id, evt) {
  throb($('comment_delete_box_'+comment_id),'deleting...');
  var url = base_url+'/delete_comment/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var field_keys = ['item_id','comment_id'];
  var field_values = [item_id,comment_id];
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('comment_delete_box_'+comment_id));
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      
      if (jsondata.messages.length > 0)
        alert(jsondata.messages.join('\n'));
      
      if (jsondata.success == 'true') {
        var deleted_comment_element =  $('item_'+item_id+'_comment_'+comment_id);
        deleted_comment_element.innerHTML = 'Deleted!';
      }
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('comment_delete_box_'+comment_id));
    new_window_show(err.req.responseText);
  });
}


function edit_comment(item_id, comment_id, evt) {
  var comment_element =  $('item_'+item_id+'_comment_'+comment_id);
  var comment_data = load_comment(item_id, comment_id);
  
  var results = '';
  results += '<div class="header button add_edit_comment">';
  results += 'Edit Comment';
  results += '</div>';
  results += draw_add_edit_comment(comment_id);

  var edit_comment_el = document.createElement('div');
  edit_comment_el.id = 'edit_item_'+item_id+'_comment_'+comment_id;
  edit_comment_el.className = 'comment';
  edit_comment_el.innerHTML = results;
  
  comment_element.parentNode.insertBefore(edit_comment_el,comment_element);
  hideElement(comment_element);
  
  $('edit_comment_'+comment_id+'_by').value = comment_data.by;
  $('edit_comment_'+comment_id+'_link').value = comment_data.link;
  $('edit_comment_'+comment_id+'_text').value = unescape(comment_data.text).replace(/&/g,'&amp;');
  
  // cancel buton
  var cancel_button = document.createElement('div');
  cancel_button.id = 'cancel_edit_comment_'+comment_id;
  cancel_button.className = 'header_button';
  cancel_button.innerHTML = 'cancel';
  edit_comment_el.insertBefore(cancel_button, edit_comment_el.childNodes[1]);
  connect(cancel_button, 'onclick', partial(self.edit_comment_cancel, item_id, comment_id));
  
  // submit button
  connect($('edit_comment_'+comment_id+'_submit_button'), 'onclick', partial(self.edit_comment_submit, item_id, comment_id));
}


function edit_comment_cancel(item_id, comment_id, evt) {
  var comment_element =  $('item_'+item_id+'_comment_'+comment_id);
  showElement(comment_element);
  
  var edit_comment_element = $('edit_item_'+item_id+'_comment_'+comment_id);
  disconnectAll($('cancel_edit_comment_'+comment_id));
  removeElement(edit_comment_element);
}


function edit_comment_submit(item_id, comment_id, evt) {
  throb($('edit_comment_'+comment_id+'_submit_button'),'Saving...');

  var url = base_url+'/update_comment/';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  
  var by = $('edit_comment_'+comment_id+'_by').value;
  var lnk = $('edit_comment_'+comment_id+'_link').value;
  var txt = $('edit_comment_'+comment_id+'_text').value;
  
  var field_keys = ['item_id','comment_id','by','link','text','t'];
  var field_values = [item_id,comment_id,by,lnk,txt,rightnow];
  
  var data = queryString(field_keys,field_values);
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    unthrob($('edit_comment_'+comment_id+'_submit_button'));
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success == 'true') {
        edit_comment_cancel(item_id, comment_id);

        var comment_el = $('item_'+item_id+'_comment_'+comment_id);
        
        var new_comment_el = document.createElement('div');
        new_comment_el.id = 'temp';
        new_comment_el.innerHTML = jsondata.comment_html;
        
        swapDOM(comment_el, new_comment_el);
        swapDOM($('temp'), $('item_'+item_id+'_comment_'+comment_id));
        add_comment_edit_links(item_id,comment_id);
        
      }
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    unthrob($('edit_comment_'+comment_id+'_submit_button'));
    new_window_show(err.req.responseText);
  });
}

function update_login_status(logged_in) {
  if (logged_in) {
    hideElement($('login_box'));
    show_login_box();
    createLoggingPane(true);
  } else {
  }
}

function update_login_box(toggle) {
  if (logged_in) {
    if ($('login_link')) { // little link style
      $('login_link').innerHTML = '';
    }
    
    var results = '';
    
    results += '<div>Logged in.</div>';
    results += '<div><span id="logout_link">logout</span></div>';
    $('login_box').innerHTML = results;
    
    connect($('logout_link'), 'onclick', this, 'logout_submit');
    showElement($('login_box'));
    
    var temp = createDOM('li', {'id':'drafts_menuitem'});
    temp.className = '';
    temp.innerHTML = '<a href="'+base_url+'/view/drafts">Drafts</a>';
    $('site_menu').appendChild(temp);
    
  } else {
    disconnectAll($('logout_link'));
    
    if ($('login_link')) { // little link style
      $('login_link').innerHTML = 'log in';
      hideElement($('login_box'));
    }
    
    var results = '';
    results += '<div>Login: <input id="login_name"/></div>';
    results += '<div>Pwd: <input type="password" id="login_pwd"/></div>';
    $('login_box').innerHTML = results;
    
    disconnectAll($('login_name'));
    disconnectAll($('login_pwd'));
    connect($('login_name'), 'onkeyup', this, 'login_keypress');
    connect($('login_pwd'), 'onkeyup', this, 'login_keypress');
    
    if ($('drafts_menuitem'))
      removeElement($('drafts_menuitem'));
  }
}

function update_edit_links() {
  if (logged_in) {
    // add new item link
    var item_element = $('add_item_link');
    var add_button = document.createElement('div');
    add_button.id = 'add_item_box';
    add_button.className = 'header_button';
    add_button.innerHTML = 'Add';
    item_element.appendChild(add_button);
    connect(add_button, 'onclick', partial(self.add_item, null));

    // edit links
    for (var l1=0;l1<item_ids.length;l1++) {
      var item_element = $('item_'+item_ids[l1]);
      var edit_button = document.createElement('div');
      edit_button.id = 'edit_box_'+item_ids[l1];
      edit_button.className = 'header_button';
      edit_button.innerHTML = 'edit';
      item_element.insertBefore(edit_button, item_element.firstChild);
      connect(edit_button, 'onclick', partial(self.edit_item, item_ids[l1], null));
    }

    // comment links
    var item_id = (page_id == '') ? item_ids[0] : page_id;
    for (var l1=0;l1<comment_ids.length;l1++) {
      add_comment_edit_links(item_id, comment_ids[l1]);
    }

    // page
    if ($('page_'+page_id)) {
      page_element = $('page_'+page_id);
      var page_edit_link = createDOM('div', {'id':'page_edit_link','class':'header_button'});
      page_edit_link.innerHTML = 'Edit';
      page_element.insertBefore(page_edit_link, page_element.firstChild);
      connect(page_edit_link, 'onclick', partial(self.edit_item, page_id, null));
    }
  } else { // remove links
    // remove item edit links
    for (var l1=0;l1<item_ids.length;l1++) {
      var item_element = $('item_'+item_ids[l1]);
      var item_edit_links = getElementsByTagAndClassName('div', 'header_button', item_element);
      for (var l2=0;l2<item_edit_links.length;l2++) {
        disconnectAll(item_edit_links[l2]);
        removeElement(item_edit_links[l2]);
      }
    }
    // remove comment edit links
    var item_id = (page_id == '') ? item_ids[0] : page_id;
    for (var l1=0;l1<comment_ids.length;l1++) {
      var comment_element_id = 'item_'+item_id+'_comment_'+comment_ids[l1];
      var comment_element = $(comment_element_id);
      comment_edit_links = getElementsByTagAndClassName('div', 'header_button', comment_element);
      for (var l2=0;l2<comment_edit_links.length;l2++) {
        disconnectAll(comment_edit_links[l2]);
        removeElement(comment_edit_links[l2]);
      }
    }

    if ($('page_'+page_id)) {
      disconnectAll($('page_'+page_id));
    }
    
    disconnectAll($('add_item_link'));
    if ($('add_item_box'))
      removeElement($('add_item_box'));
      
    // add comment links for editable comments
    var item_id = (page_id == '') ? item_ids[0] : page_id;
    for (var l1=0;l1<editable_comments.length;l1++) {
      var comment_element_id = 'item_'+item_id+'_comment_'+editable_comments[l1];
      var comment_element = $(comment_element_id);
      
      var edit_link = document.createElement('div');
      edit_link.id = 'comment_edit_box_'+editable_comments[l1];
      edit_link.className = 'header_button';
      edit_link.innerHTML = 'edit';
      comment_element.insertBefore(edit_link, comment_element.firstChild.nextSibling.nextSibling);
      connect(edit_link, 'onclick', partial(self.edit_comment, item_id, editable_comments[l1]));
      
      var delete_link = document.createElement('div');
      delete_link.id = 'comment_delete_box_'+editable_comments[l1];
      delete_link.className = 'header_button';
      delete_link.innerHTML = 'delete';
      comment_element.insertBefore(delete_link, edit_link.nextSibling.nextSibling);
      connect(delete_link, 'onclick', partial(self.delete_comment, item_id, editable_comments[l1]));
    }
  }

  if ($('add_comment')) {
    var results = '';
    results += '<div class="header button add_edit_comment">';
    results += 'Add Comment';
    results += '</div>';
    
    results += draw_add_edit_comment('new');

    $('add_comment').innerHTML = results;
    $('add_comment').className = 'comment';
    connect($('add_new_comment_submit_button'), 'onclick', self.add_comment);
  }
  
  if ($('create_this_page')) {
    if (logged_in) {
      showElement($('create_this_page'));
      connect($('create_this_page'), 'onclick', partial(self.add_item, 'page'));
    } else {
      hideElement($('create_this_page'));
      disconnectAll($('create_this_page'));
    }
  }
}

function check_login_status() {
  return false;
}

function props(o) {
  var results = '';
  for (var p in o)
    results += p+':'+o[p]+'\n';
  return results;
}

function new_window_show(text) {
  info_window = this.open('', 'info_window', 'resizable=yes,status=yes,scrollbars=yes,locationbar=yes,location=yes,menubar=yes,toolbar=yes,width=1000,height=1000');
  
  if (text.match(/^http/)) {
    info_window.location = text;
  } else {
    doc = info_window.document;
    doc.open('text/html');
    doc.write(text);
    doc.close();
  }
  info_window.focus();
}

function throb(el, text) {
  if (!el) return;
  unthrob_element[el.id] = el;
  unthrob_text[el.id] = el.innerHTML;
  el.innerHTML = '<img class="minithrobber" style="vertical-align:middle;" src="'+base_url+'/throbber.gif">'+text;
}

function unthrob(el) {
  if (unthrob_element[el.id])
    unthrob_element[el.id].innerHTML = unthrob_text[el.id];
  
  unthrob_element[el.id] = null;
  unthrob_text[el.id] = null;
}

function files_dialog() {
  throb($('files_dialog_box'),'Getting Files...');

  // appear dialog box
  var contents = '';
  contents += '<div id="upload_files" class="upload_files_button">Upload files</div>';
  contents += '<div id="subdirs">subdir:';
  contents += '<select id="subdir_select">';
  contents += '<option class="none" value="">/</option>';
  
  contents += '</select>';
  contents += '<input id="subdir" value=""/>';
  contents += '</div>';
  contents += '<div id="filesDisplay">';
	contents += '<ul id="mmUploadFileListing"></ul><br/>';
	contents += '</div>';
	contents += '<div id="filelist_surround"> </div>';
  contents += '<div id="SWFUpload"></div>';

  dialog_box.setTitle('Files');
  dialog_box.setContents(contents);
  dialog_box.anchor($('site_menu'));
  dialog_box.element.style.display = 'block';
  
  var s_id = getcookie('s_id');
  
  // init SWFupload object
  mmSWFUpload.init({
      //debug : true,
  		base_url : base_url,
  		allowed_filetypes : '*',
  		allowed_filesize : 100000,
  		upload_backend : base_url+'/upload_file/'+s_id+'/',
  		target : "SWFUpload",
      upload_start_callback : 'uploadStart',
		  upload_progress_callback : 'uploadProgress',
		  upload_complete_callback : 'uploadComplete',
		  upload_error_callback : 'uploadError',
		  upload_cancel_callback : 'uploadCancel',
		  upload_queue_complete_callback : 'uploadQueueComplete'
  	});
  
  connect($('upload_files'), 'onclick', upload_files);
  
  // load filelist
  var url = base_url+'/js/get_files/';
  var req = getXMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  unthrob($('files_dialog_box'));
  jsondata = eval('(' + req.responseText + ')');
  if (jsondata.success == 'true') {
    refresh_filelist(jsondata.files); // display filelist
  }
}

function init_swfupload(sid,subdir) {
}


function refresh_filelist(files) {
  var subdirs = {};
  // disconnect actions of current list
  for (var l1=0;l1<files.length;l1++) {
    if (files[l1]['subdir'] && files[l1]['subdir'] != '')
      subdirs[files[l1]['subdir']] = true;
    
    var fname = files[l1]['name'];
    var fid = fname.replace(/\s/g,'');
    if ($('file_link_'+fid)) {
      disconnectAll($('file_link_'+fid));
      disconnectAll($('delete_file_'+fid));
    }
  }
  
  // redraw filelist
  $('filelist_surround').innerHTML = draw_filelist(files,subdirs,'');
  
  // populate subdirs dropdown
  subdir_select = $('subdir_select');
  var subdir_index = 1
  for (subdir in subdirs) {
    subdir_select.options[subdir_index] = new Option('/'+subdir,subdir);
    subdir_index++;
  }
  subdir_select.selectedIndex = 0;
  connect($('subdir_select'), 'onchange', partial(self.chdir, files, subdirs));
  
  // connect new actions
  connect_filelist(files,subdirs,'');
}


function connect_filelist(files, subdirs, evt) {
  for (var l1=0;l1<files.length;l1++) {
    if (files[l1]['subdir'] && files[l1]['subdir'] != current_subdir) continue;
    if (current_subdir == files[l1]['name']) continue;

    var fname = files[l1]['name'];
    var fid = fname.replace(/\s/g,'');
    var file_subdir = (current_subdir == '') ? '' : current_subdir+'/';

    if (files[l1]['subdir'] == current_subdir && !subdirs[fname]) {
      connect($('file_link_'+fid), 'onclick', partial(self.insert_file_ref, file_subdir+fname));
      connect($('delete_file_'+fid), 'onclick', partial(self.delete_file, fname, files[l1]['subdir']));
    }
  }
}


function chdir(files, subdirs, evt) {
  current_subdir = get_selected($('subdir_select'));
  $('subdir').value = current_subdir;
  $('filelist_surround').innerHTML = draw_filelist(files,subdirs);
  connect_filelist(files,subdirs);
}

function draw_filelist(files, subdirs) {
  var results = '';
  results += '<table id="filelist">';
  
  results += '<tr><th>File</th><th>Date</th><th>Size</th><th>Actions</th></tr>';
  
  if (current_subdir != '') {
    results += '<tr class="subdir"">';
    results += '<td class="name" colspan="4"><span class="file_link" id="file_link___toplevel">..</span>';
    results += '</td>';
    results += '</tr>';
  }
  
  for (var l1=0;l1<files.length;l1++) {
    if (files[l1]['subdir'] && files[l1]['subdir'] != '' && files[l1]['subdir'] != current_subdir) continue;
    if (files[l1]['subdir'] == '' && current_subdir != '') continue;
    if (current_subdir == files[l1]['name']) continue;
  
    var fname = files[l1]['name'];
    var fid = fname.replace(/\s/g,'');
    var size = files[l1]['size'];
    var timestamp = files[l1]['timestamp'];
    var nice_date = new Date(timestamp*1000);
	  nice_date = (nice_date.getMonth()+1)+'-'+nice_date.getDate()+'-'+nice_date.getFullYear();
    
    var file_subdir = (current_subdir == '') ? '' : current_subdir+'/';

    var tr_class = (array_contains(newly_uploaded_files,fname)) ? 'file new' : 'file';
    
    if (!subdirs[fname]) {
      results += '<tr class="'+tr_class+'" id="file_'+fid+'">';
      results += '<td class="name"><span class="file_link" id="file_link_'+fid+'">'+fname+'</span>';
      if (is_image(fname))
        results += '<br/><img class="image_file_thumb" src="'+base_url+'/files/'+file_subdir+fname+'"/>';
      results += '</td>';
 
      results += '<td class="date">'+nice_date+'</td>';
      results += '<td class="size">'+nice_size(size)+'</td>';
      results += '<td class="actions"><div id="delete_file_'+fid+'" class="delete_file">.</div></td>';
      results += '</tr>';
    }
  }
  results += '</table>';
  return results;
}

function insert_file_ref(fname, evt) {
  var fid = fname.replace(/\s/g,'');
  var txt = '{{'+fname+'}}';
  insertAtCursor($(current_field_id),txt);
}

function delete_file(fname, subdir, evt) {
  $('mmUploadFileListing').innerHTML = '';
  var fid = fname.replace(/\s/g,'');
  throb($('delete_file_'+fid),'Deleting...');
  
  var field_keys = ['name','subdir'];
  var field_values = [fname, subdir];
  var data = queryString(field_keys,field_values);
  
  var url = base_url+'/delete_file';
  var req = getXMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
  var d = sendXMLHttpRequest(req, data);
  d.addCallback(function(rsp) {
    try {
      jsondata = eval('(' + rsp.responseText + ')');
      if (jsondata.success = 'true') {
        refresh_filelist(jsondata.files);  
      }
    } catch (e) {log(e);}
  });
  
  d.addErrback(function(err) {
    new_window_show(err.req.responseText);
  });
}


function upload_files() {
  current_upload_subdir = $('subdir').value;
  current_subdir = current_upload_subdir;
  
  $('mmUploadFileListing').innerHTML = '';
  mmSWFUpload.callSWF();
  newly_uploaded_files = [];
}

function uploadStart(fileObj) {
	$('filesDisplay').style.display = 'block';
	var progress_text = '<li id="'+fileObj.name+'" class="uploading">'+fileObj.name+'<span id="'+fileObj.name+'progress" class="progressBar"></span></li>'
	$('mmUploadFileListing').innerHTML += progress_text;
}

function uploadProgress(fileObj, bytesLoaded) {
	var progress = $(fileObj.name + 'progress');
	var percent = Math.ceil((bytesLoaded / fileObj.size) * 100)
	progress.style.width = percent + 'px';
}

function uploadComplete(fileObj) {
	$(fileObj.name).className = 'uploadDone';
	$(fileObj.name).innerHTML += " " + (Math.ceil(fileObj.size / 1000)) + ' kb';
  newly_uploaded_files.push(fileObj.name);
}

function uploadError(errorCode) {
  var error_messages = {'-10':'HTTP error', '-20':'No backend file specified', '-30':'IO error', '-40':'Security error', '-50':'Filesize too big'};
                        
  $("filesDisplay").style.display = 'block';
  
  var message = 'upload error: '+errorCode+'-'+ error_messages[errorCode+'']
 
  $("filesDisplay").innerHTML = message;
}

function uploadCancel(fileObj) {
  //log('uploadCancel '+list_properties(fileObj));
}

function uploadQueueComplete() {
  // load filelist
  if (current_upload_subdir == '') {
    log('about to refresh files');
    var url = base_url+'/js/get_files/';
    var req = getXMLHttpRequest();
    req.open("GET", url, false);
    req.send(null);
    jsondata = eval('(' + req.responseText + ')');
    if (jsondata.success = 'true') {
      refresh_filelist(jsondata.files); // display filelist
    }
 
    // scrollto currently doesn't work with max-height set on filelist_surround :(
    var fid = newly_uploaded_files[0].replace(/\S/g,'');
    new ScrollTo('file_'+fid,{'delay':0,'duration':0});
  } else {
    var url = base_url+'/move_files/';
    var req = getXMLHttpRequest();
    req.open("POST", url, false);
    req.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=UTF-8');
    var field_keys = ['files','subdir'];
    var field_values = [newly_uploaded_files, current_upload_subdir];
    var data = queryString(field_keys,field_values);
    req.send(data);
    jsondata = eval('(' + req.responseText + ')');
    if (jsondata.success == 'true') {
      refresh_filelist(jsondata.files); // display filelist
    }
  }
}

function nice_size(num) {
  if (num > 1048576)
    return (Math.floor(num*10 / 1048576))/10+'M'
    
  if (num > 10240)
    return Math.floor(num/ 10240)+'k'
    
  if (num > 1024)
    return Math.floor(num / 1024)+'k'
  
  return num+'b'
}

function is_image(fname) {
  if (fname.match(/\.(gif|jpe?g|png|)$/))
    return true;
  return false;
}

function list_properties(o) {
  var results = ''+o+'\n';
  for (p in o)
    results += p+':'+o[p]+'\n';
  return results; 
}

function insertAtCursor(el, txt) {
  if (!el) return;
  
  if (document.selection) {  //IE
    el.focus();
    sel = document.selection.createRange();
    sel.text = txt;
  } else if (el.selectionStart || el.selectionStart == '0') { // FF
    var startPos = el.selectionStart;
    var endPos = el.selectionEnd;
    el.value = el.value.substring(0, startPos)+ txt + el.value.substring(endPos, el.value.length);
  } else {
    el.value += txt;
  }
}


function array_contains(ar, el) {
  for(var i=0;i<ar.length;i++) {
    if(el == ar[i]) return true;
  }
  return false;
}

function getcookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
  
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function get_selected(el) {
  return el.options[el.selectedIndex].value;
}

function upate_loggingPane() {
  // enable lines below if you're going to debug javascript
  var popout_window = true;
  
  // all the time
  //loggingPane = createLoggingPane(!popout_window);
  
  // only when logged in
  //if (logged_in) loggingPane = createLoggingPane(!popout_window);
}
