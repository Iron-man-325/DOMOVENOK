if ("I'm too lazy to remove spaces from every line") {
  // First of all, read comments in the function createField




  /** PARAMS:
   * @param {object Array} elements - array of elements, created by function createInnerField
   * @param {number} n - number of current (added) field. You can use it only here.
   * @param {string} attr_id - main part of id-attribute in the whole group of the added elements
   */

  function setId(elements, n, attr_id) {
    /* Function to work with all that requires n (number of current field).
     * It needs for fast and correct work of function deleteField.
     * If you want to use it, you must move ALL usages of n HERE.
     * Works only if elements array changes; else -
     * elements recreating with the createInnerField function many times.
     */

    return elements; // Returns modified array of elements... but...
    // JS saves all changes made by function in array given as parameter
  }

  /** PARAMS:
   * @param {number} n - number of current (added) field. Highly recomended use it only in setId.
   * @param {string} attr_id - main part of id-attribute in the whole group of the added elements
   */

  function createInnerField(n, attr_id) {
    // This function creates <somehtml>...</somehtml> from scheme - field(s)
    // There can be not only one element, because
    // Function returns an array of standart JS elements (document.createElement('...')).

    // n - number of current field. There's an ANOTHER FUNCTION to work with it
    // attr_id - main part of id-attribute in the whole group of the created elements

    var elements = [];
    // Add HTML-elements to this array one by one
    // DON'T USE VARIABLE n IN THIS FUNCTION

    elements.append(document.createElement('input'));
    switch (attr_id) {  // switch exists in JS; don't forget to use it.
      case "a":
        elements[0].type = "text";
        elements[0].className = "group-input";
        break;
      case "b":
        elements[0].type = "number"
        elements[0].className = "count-input";
        break;
      default:
        break;
    }

    setId(elements, n, attr_id);  // You can move usages of n here if 

    /* Usages of n only in other function (setId) needs
     * for optimization of the deleteField function.
     * If you don't care about it -
     * set setId function's return to undefined
     * and only then you can use n here.
     */

    return elements;
  }

  function createField(attr_id, max_fields, n, add_to_node_id) {
    // Function for the "add" button
    // Adds this construction to the node with attribute id="[add_to_id]":
    /* <div class='row justify-content-between' id='div_[attr_id][n]'>
     *   <somehtml>...</somehtml>
     *   <div class='col-1'>
     *     <input type='button' onclick='deleteField([n], [attr_id])' value='-'>
     *   </div>
     * </div>
     */
    // Where:
    // attr_id - name and id in the whole group of the created elements. Required
    // max_fields - maximum fields allowed for this group (if undefined, max_fields = 420)
    /* n - count starting with n-th field (EXAMPLE: you have 2 base fields in
     * your page, so you need to add starting with 3-rd -> call with n = 3)
     * (if undefined, n = 1)
     */
    // somehtml - (your own) HTML created by the function createInnerField

    if (typeof attr_id !== 'string' || attr_id === "") {
      attr_id = "var";
    }
    if (typeof max_fields !== 'number' || max_fields % 1 !== 0 || max_fields < 1) {
      max_fields = 420;
    }
    if (typeof n !== 'number' || n % 1 !== 0 || n > max_fields || n < 1) {
      n = 1;
    }
    if (typeof add_to_id !== 'string' || attr_id === "") {
      add_to_id = "add_to";
    }

    var field;
    while (document.getElementById('div_' + attr_id + n) && n <= max_fields) { n++; }
    if (n > max_fields) {
      if (!(document.getElementById(attr_id + '_error_too_many_fields'))) {
        error = document.createElement('p');
        error.id = attr_id + '_error_too_many_fields';
        error.style = 'color: #fe0202; font-size: 15px;';
        error.innerText = "Too many fields. You can't add more than " + max_fields + " fields. (слишком много полей)";
        document.getElementById('fields').appendChild(error);
      }
    } else {
      field = document.createElement('div');
      field.className = 'row justify-content-between';
      field.id = 'div_' + attr_id + n;

      var inner = createInnerField(n, attr_id);

      var div = document.createElement('div');
      div.className = 'col-1';
      var deleteButton = document.createElement('input');
      deleteButton.type = 'button';
      deleteButton.setAttribute('onclick', 'deleteField("' + n + '", "' + attr_id + '", "' + max_fields + '")');
      deleteButton.value = '-';
      div.appendChild(deleteButton);

      if (typeof inner === 'object') {
        for (var i = 0; i < inner.length; i++) field.appendChild(inner[e]);
      }
      field.appendChild(div);
      document.getElementById(add_to_id).insertAdjacentElement('beforebegin', field);
    }
  }

  function deleteField(id, attr_id, max_fields) {
    // Function for the "delete" ("-") button
    // Removes the element <div id="div_[attr_id][id]" ...>...</div>
    if (typeof attr_id !== 'string' || attr_id === "") {
      attr_id = "var";
    }
    document.getElementById('div_' + attr_id + id).remove();
    if (document.getElementById(attr_id + '_error_too_many_fields')) {
      document.getElementById(attr_id + '_error_too_many_fields').remove();
    }
    var field = document.getElementById('div_' + attr_id + (Number(id) + 1));
    while (field && Number(id) <= max_fields) {
      var inner = field.children;
      var deleteButton = inner.pop();
      deleteButton.setAttribute('onclick', 'deleteField("' + id + '", "' + attr_id + '", "' + max_fields + '")');
      inner = setId(inner, id, attr_id);
      if (inner == field.child) inner = createInnerField(n, attr_id);
      inner.append(deleteButton);
      field.id = 'div_' + attr_id + id;
      id++;
      field = document.getElementById('div_' + attr_id + (Number(id) + 1));
    }
  }

  // © seryi_otten0k, 2025. All rights reserved... maybe
}
