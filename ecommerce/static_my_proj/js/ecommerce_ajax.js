$(document).ready(function() {

  // Contact form handler
  var contactForm = $(".contact-form");
  var contactFormMethod = contactForm.attr("method");
  var contactFormEndPoint = contactForm.attr("action");

  function submitLoader(submitBtn, defaultText, doSubmit) {
    if (doSubmit) {
      submitBtn.addClass("disabled");
      submitBtn.html(`<i class="fa-spin fas fa-spinner"></i> Sending...`);
    } else {
      submitBtn.removeClass("disabled");
      submitBtn.html(defaultText);
    }
  }

  contactForm.submit(function(event) {
    event.preventDefault();
    var contactFormSubmitBtn = contactForm.find("[type='submit']");
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text();
    var contactFormData = contactForm.serialize();
    var thisForm = $(this);
    submitLoader(contactFormSubmitBtn, "", true);
    $.ajax({
      url: contactFormEndPoint,
      method: contactFormMethod,
      data: contactFormData,
      success: function(data) {
        contactForm[0].reset();
        $.alert({
          title: "Success!",
          content: data.message,
          theme: "modern"
        });
        setTimeout(function() {
          submitLoader(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
        }, 500);
      },
      error: function(error) {
        var errorData = error.responseJSON;
        var error_messages = "";
        $.each(errorData, function(key, value) {
          error_messages += `<b>${key}:</b> ${value[0].message}<br>`;
        });
        $.alert({
          title: "Sorry!",
          content: error_messages,
          theme: "modern"
        });
        console.log("error");
        setTimeout(function() {
          submitLoader(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
        }, 500);
      },
    });
  });

  // Auto Search
  var searchForm = $(".search-form");
  var searchInput = searchForm.find("[name='q']");
  var searchBtn = searchForm.find("[type='submit']");
  var typingTimer;
  var typingInterval = 500;

  searchInput.keyup(function(event) {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(performSearch, typingInterval);
  });
  searchInput.keydown(function(event) {
    clearTimeout(typingTimer);
  });

  function searchLoader() {
    searchBtn.addClass("disabled");
    searchBtn.html(`<i class="fa-spin fas fa-spinner"></i> Searching...`);
  }

  function performSearch() {
    searchLoader();
    var query = searchInput.val();
    setTimeout(function() {
      window.location.href = "/search/?q=" + query;
    }, 1000);
  }

  // Cart add products
  var productForm = $(".form-product-ajax");

  function getOwnedProduct(productId, submitSpan) {
    var actionEndpoint = "/orders/api/endpoint/verify/ownership/";
    var method = "GET"
    var data = {
      'product_id': productId
    };
    var isOwner;
    $.ajax({
      url: actionEndpoint,
      method: method,
      data: data,
      success: function(data) {
        if (data.owner) {
          isOwner = true;
          submitSpan.html(`<a class="btn btn-warning my-3" href="/library/">In Library</a>`);
        } else {
          isOwner = false;
        }
      },
      error: function(errorData) {
        console.log(errorData);
      }
    });
    return isOwner;
  }

  $.each(productForm, function(index, object) {
    var thisForm = $(this);
    var submitSpan = thisForm.find(".submit-span");
    var productInput = thisForm.find("[name='product_id']");
    var productId = productInput.attr("value");
    var productIsDigital = productInput.attr("data-is-digital");
    var isUser = thisForm.attr("data-user");
    
    if (productIsDigital && isUser) {
      var isOwned = getOwnedProduct(productId, submitSpan);
    }
  });

  productForm.submit(function(event) {
    event.preventDefault();
    var thisForm = $(this);
    // var actionEndpoint = thisForm.attr("action");
    var actionEndpoint = thisForm.attr("data-endpoint");
    var httpMethod = thisForm.attr("method");
    var formData = thisForm.serialize();

    $.ajax({
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      success: function(data) {
        var submitSpan = thisForm.find(".submit-span")
        if (data.added) {
          submitSpan.html(`
          <a class="btn btn-link" href="/cart/">In Cart</a> <button type="submit" class="btn btn-danger my-3">Remove</button>
          `);
        } else {
          submitSpan.html(`<button type="submit" class="btn btn-success my-3">Add to Cart</button>`);
        }
        var navbarCount = $(".navbar-cart-count");
        navbarCount.text (data.cartItemCount)
        var currentPath = window.location.href;
        if (currentPath.indexOf("cart") !== -1) {
          refreshCart();
        }
      },
      error: function(errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred",
          theme: "modern"
        });
        console.log("error");
      }
    });
  });

  function refreshCart() {
    var currentUrl = window.location.href;
    var cartTable = $(".cart-table");
    var cartBody = cartTable.find(".cart-body");
    var productRows = cartBody.find(".cart-products");

    var refreshCartUrl = "/api/cart/";
    var refreshCartMethod = "GET";
    var data = {};
    $.ajax({
      url: refreshCartUrl,
      method: refreshCartMethod,
      data: data,
      success: function(data) {
        console.log("success");
        var hiddenCartItemRemoveForm = $(".cart-item-remove-form");
        var hiddenCartQuantityForm = $(".cart-item-quantity-form");
        if (data.products.length > 0) {
          productRows.html("")
          var i = data.products.length
          $.each(data.products, function(index, element) {
            var newCartItemRemove = hiddenCartItemRemoveForm.clone();
            var newCartQuantityUpdate = hiddenCartQuantityForm.clone();
            newCartItemRemove.css("display", "block"); // newCartItemRemove.removeClass("hidden-class")
            newCartItemRemove.find(".cart-item-product-id").val(element.id);
            newCartQuantityUpdate.css("display", "block");
            newCartQuantityUpdate.find(".cart-item-product-id").val(element.id)
            cartBody.prepend(`
            <tr>
              <th scope="row">${i}</th>
              <td><a href="${element.url}">${element.name}</a>${newCartItemRemove.html()}</td>
              <td>${newCartQuantityUpdate.html()}</td>
              <td id="product-price-${element.id}">${element.price}</td>
            </tr>
            `);
            i--;
          });
          cartBody.find(".cart-subtotal").text(data.subtotal);
          cartBody.find(".cart-total").text(data.total);
        } else {
          window.location.href = currentUrl;
        }
      },
      error: function(errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred",
          theme: "modern"
        });
        console.log(errorData);
      }
    });
  }

  var quantityForm = $(".form-product-quantity-ajax");
  // var hasIncreased = false;
  // var hasDecreased = false;
  var oldValue = 0;
  var currentValue = 0;
  $(".cart-product-quantity").focusout(function() {
    var direction = this.defaultValue < this.value
    oldValue = parseInt(this.defaultValue);
    currentValue = parseInt(this.value);
    this.defaultValue = this.value;
    // if (direction) {
    //   hasIncreased = true;
    //   hasDecreased = false;
    // }
    // else {
    //   hasDecreased = true;
    //   hasIncreased = false;
    // }
  });
  quantityForm.submit(function(event) {
    event.preventDefault();
    var cartTable = $(".cart-table");
    var cartBody = cartTable.find(".cart-body");
    var thisForm = $(this);
    var productQty = parseInt(thisForm.find(".cart-product-quantity").val());
    var productId = thisForm.find(".cart-item-product-id").val();

    var refreshCartQuantityUrl = '/api/cart/quantity/'
    var refreshCartQuantityMethod = "POST"
    var data = {
      'product_id': productId,
      'product_qty': productQty,
      'old_value': oldValue,
      'current_value': currentValue,
      // 'has_increased': hasIncreased,
      // 'has_decreased': hasDecreased,
    };
    $.ajax({
      url: refreshCartQuantityUrl,
      method: refreshCartQuantityMethod,
      data: data,
      success: function(data){
        cartBody.find(".cart-subtotal").text(data.subtotal);
        cartBody.find(".cart-total").text(data.total);
        cartBody.find(`#product-price-${productId}`).text(`$${data.original_price} X ${data.product_qty} = $${data.new_price}`);
      },
      error: function(errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred",
          theme: "modern"
        });
        console.log(errorData);
      }
    });
  });

  var finalizeCheckoutForm = $(".finalize-checkout");
  
  function checkoutLoader(checkoutBtn, defaultTxt, doCheckout) {
    if (doCheckout) {
      checkoutBtn.addClass("disabled");
      checkoutBtn.html(`<i class="fa-spin fas fa-spinner"></i> Finalizing...`);
    } else {
      checkoutBtn.removeClass("disabled");
      checkoutBtn.html(defaultTxt);
    }
  }
  finalizeCheckoutForm.on('submit', function() {
    var thisForm = $(this);
    var finalizeCheckoutButton = thisForm.find("[type='submit']");
    var finalizeCheckoutBtnTxt = finalizeCheckoutButton.text();
    checkoutLoader(finalizeCheckoutButton, "", true);
    setTimeout(function() {
      checkoutLoader(finalizeCheckoutButton, finalizeCheckoutBtnTxt, false)
    }, 8500);
  });

});