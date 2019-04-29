$(document).ready(function() {
    var stripeFormModule = $('.stripe-payment-form');
    var stripeModuleToken = stripeFormModule.attr("data-token");
    var stripeModuleNextUrl = stripeFormModule.attr("data-next-url");
    var stripeModuleBtnTitle = stripeFormModule.attr("data-btn-title") || "Add Card";
    var stripeTemplate = $.templates("#stripeTemplate");
    var stripeTemplateDataContext = {
        publishKey: stripeModuleToken,
        nextUrl: stripeModuleNextUrl,
        btnTitle: stripeModuleBtnTitle
    };
    var stripeTemplateHtml = stripeTemplate.render(stripeTemplateDataContext);
    stripeFormModule.html(stripeTemplateHtml);

    var paymentForm = $(".payment-form")
    if (paymentForm.length > 1) {
        alert("Only one payment form allowed");
        paymentForm.css("display", "none");
    } else if (paymentForm.length === 1) {
        // Create a Stripe client.
        var pubKey = paymentForm.attr("data-token");
        var nextUrl = paymentForm.attr("data-next-url");
        var stripe = Stripe(pubKey);

        // Create an instance of Elements.
        var elements = stripe.elements();

        // Custom styling can be passed to options when creating an Element.
        // (Note that this demo uses a wider set of styles than the guide below.)
        var style = {
            base: {
                color: '#32325d',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': {
                color: '#aab7c4'
                }
            },
            invalid: {
                color: '#fa755a',
                iconColor: '#fa755a'
            }
        };

        // Create an instance of the card Element.
        var card = elements.create('card', {style: style});

        // Add an instance of the card Element into the `card-element` <div>.
        card.mount('#card-element');

        // Handle real-time validation errors from the card Element.
        card.addEventListener('change', function(event) {
            var displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });

        // Handle form submission.
        var form = $('#payment-form');
        var btnLoad = form.find(".btn-load");
        var btnLoadDefaultHtml = btnLoad.html();
        var btnLoadDefaultClasses = btnLoad.attr("class");

        form.on('submit', function(event) {
            btnLoad.blur();
            event.preventDefault();
            var errorHtml = `<i class="fas fa-exclamation-triangle"></i> Card details empty`;
            var loadingHtml = `<i class="fa-spin fas fa-spinner"></i> Loading...`;
            var errorClasses = "btn btn-danger btn-lg disabled my-3";
            var loadingClasses = "btn btn-success btn-lg disabled my-3";
            var currentTimeout;

            stripe.createToken(card).then(function(result) {
                if (result.error) {
                    // Inform the user if there was an error.
                    var errorElement = $('#card-errors');
                    errorElement.textContent = result.error.message;
                    currentTimeout = displayBtnStatus(btnLoad, errorHtml, errorClasses, 1500, currentTimeout);
                } else {
                    // Send the token to your server.
                    currentTimeout = displayBtnStatus(btnLoad, loadingHtml, loadingClasses, 10000, currentTimeout);
                    stripeTokenHandler(result.token, nextUrl);
                }
            });
        });

        function displayBtnStatus(element, newHtml, newClasses, loadTime, timeout) {
            // if (timeout) {
            //     clearTimeout(timeout);
            // }
            if (!loadTime) {
                loadTime = 1500;
            }
            element.html(newHtml);
            element.removeClass(btnLoadDefaultClasses);
            element.addClass(newClasses);
            return setTimeout(function() {
                element.html(btnLoadDefaultHtml);
                element.removeClass(newClasses);
                element.addClass(btnLoadDefaultClasses);
            }, loadTime);
        }

        // var form = document.getElementById('payment-form');
        // form.addEventListener('submit', function(event) {
        //     event.preventDefault();
        //     var errorHtml = `<i class="fa fa-warning></i> An error occurred`;
        //     var loadingHtml = `<i class="fa-spin fa-spinner></i> Loading...`;
        //     var errorClasses = `btn btn-danger btn-lg disabled my-3`;
        //     var loadingClasses = `btn btn-success btn-lg disabled my-3`;
        //     var loadTime = 1500;

        //     stripe.createToken(card).then(function(result) {
        //         if (result.error) {
        //             // Inform the user if there was an error.
        //             var errorElement = document.getElementById('card-errors');
        //             errorElement.textContent = result.error.message;
        //         } else {
        //             // Send the token to your server.
        //             stripeTokenHandler(result.token, nextUrl);
        //         }
        //     });
        // });

        function redirectToNext(nextPath, timeOffset) {
            if (nextPath) {
                setTimeout(function() {
                    window.location.href = nextPath;
                }, timeOffset);
            }
        }

        // Submit the form with the token ID.
        function stripeTokenHandler(token, nextUrl) {
            console.log(token.id);
            console.log(nextUrl);
            var paymentMethodEndpoint = "/billing/payment-method/create/";
            var data = {
                "token": token.id
            };
            $.ajax({
                data: data,
                url: paymentMethodEndpoint,
                method: "POST",
                success: function(data) {
                    var successMsg = data.message || "Success! Your card was added"
                    card.clear();
                    if (nextUrl) {
                        successMsg += `<br><br><i class="fa-spin fas fa-spinner"></i> Redirecting...`;
                    }
                    if ($.alert) {
                        $.alert(successMsg);
                    } else {
                        alert(successMsg);
                    }
                    btnLoad.html(btnLoadDefaultHtml);
                    btnLoad.attr("class", btnLoadDefaultClasses);
                    redirectToNext(nextUrl, 1500);
                },
                error: function(error) {
                    console.log(error);
                    $.alert({title: "An error occurred", content: "Please try adding your card again"});
                    btnLoad.html(btnLoadDefaultHtml);
                    btnLoad.attr("class", btnLoadDefaultClasses);
                }
            });

            // Insert the token ID into the form so it gets submitted to the server
            // var form = document.getElementById('payment-form');
            // var hiddenInput = document.createElement('input');
            // hiddenInput.setAttribute('type', 'hidden');
            // hiddenInput.setAttribute('name', 'stripeToken');
            // hiddenInput.setAttribute('value', token.id);
            // form.appendChild(hiddenInput);

            // // Submit the form
            // form.submit();
        }
    }
});