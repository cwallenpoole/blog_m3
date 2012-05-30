

function DialogBox(properties) {

  this.id = (properties['id']) ? properties['id'] : null;
  this.title = (properties['title']) ? properties['title'] : '';
  this.images_url = (properties['images_url']) ? properties['images_url'] : '';
  this.element_id = (properties['element_id']) ? properties['element_id'] : null;
  this.contents = properties['contents'];
  this.element = document.createElement('div');     // the DOM element that holds the dialog box
  this.element.style.display = "none";
  this.element.className += "dialog_box";
  
  if (this.element_id) {
    this.element.id = this.element_id;
  } else {
    this.element.id = "dialog_box";
    if (this.id) this.element.id += "_"+this.id;
  }
  
  document.getElementsByTagName("body").item(0).appendChild(this.element);
  var temp = '<div class="header" id="'+this.element.id+'_header"> <span id="'+this.element.id+'_hide" class="close"><img class="dialog_box_close_icon" src="'+this.images_url+'close_button1.gif" alt="[X]"/></span><span class="title" id="'+this.element.id+'_title">'+this.title+'</span></div>';
  temp += '<div class="contents" id="'+this.element.id+'_contents"></div>';
  temp += '<br style="clear:both;"/>';
  temp += '</div>';
  this.element.innerHTML = temp;
  
  this.hide_element = document.getElementById(this.element.id+"_hide");
  
  this.reset = function()  {
    document.getElementById(this.element.id+"_title").innerHTML = "";
    document.getElementById(this.element.id+"_contents").innerHTML = "";
  }
  
  this.setContents = function(contents) {
    document.getElementById(this.element.id+"_contents").innerHTML = contents;
  }
  
  this.setTitle = function(title) {
    document.getElementById(this.element.id+"_title").innerHTML = title;
  }
  
  this.closeDialogBox = function(evt) {
    this.element.style.display = "none";
  }
  
  this.anchor = function(el, evt) {
    if (!el) { // anchor to mouse cursor
      this.element.style.left = '100px';
      if (evt)
        this.element.style.top = (evt.mouse().page.y-10)+"px";
    } else {
      setElementPosition(dialog_box.element, getElementPosition(el));
    }
  }
  
  // functions must be declared before being connected to 
  connect(this.hide_element, 'onclick', this, 'closeDialogBox'); 

}
