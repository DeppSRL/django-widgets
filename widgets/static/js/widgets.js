var LOADER_NS = 'widgets_loader_ns';

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        'use strict';
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

if (!Array.prototype.forEach) {
    Array.prototype.forEach = function (fn, scope) {
        'use strict';
        var i, len;
        for (i = 0, len = this.length; i < len; ++i) {
            if (i in this) {
                fn.call(scope, this[i], i, this);
            }
        }
    };
}

var locateWidgetElements = function (className, tag, elm) {
    /*
     Developed by Robert Nyman, http://www.robertnyman.com
     Code/licensing: http://code.google.com/p/getelementsbyclassname/
     */
    var getElementsByClassName;
    if (document.getElementsByClassName) {
        getElementsByClassName = function (className, tag, elm) {
            elm = elm || document;
            var elements = elm.getElementsByClassName(className),
                nodeName = (tag) ? new RegExp("\\b" + tag + "\\b", "i") : null,
                returnElements = [],
                current;
            for (var i = 0, il = elements.length; i < il; i += 1) {
                current = elements[i];
                if (!nodeName || nodeName.test(current.nodeName)) {
                    returnElements.push(current);
                }
            }
            return returnElements;
        };
    }
    else if (document.evaluate) {
        getElementsByClassName = function (className, tag, elm) {
            tag = tag || "*";
            elm = elm || document;
            var classes = className.split(" "),
                classesToCheck = "",
                xhtmlNamespace = "http://www.w3.org/1999/xhtml",
                namespaceResolver = (document.documentElement.namespaceURI === xhtmlNamespace) ? xhtmlNamespace : null,
                returnElements = [],
                elements,
                node;
            for (var j = 0, jl = classes.length; j < jl; j += 1) {
                classesToCheck += "[contains(concat(' ', @class, ' '), ' " + classes[j] + " ')]";
            }
            try {
                elements = document.evaluate(".//" + tag + classesToCheck, elm, namespaceResolver, 0, null);
            }
            catch (e) {
                elements = document.evaluate(".//" + tag + classesToCheck, elm, null, 0, null);
            }
            while ((node = elements.iterateNext())) {
                returnElements.push(node);
            }
            return returnElements;
        };
    }
    else {
        getElementsByClassName = function (className, tag, elm) {
            tag = tag || "*";
            elm = elm || document;
            var classes = className.split(" "),
                classesToCheck = [],
                elements = (tag === "*" && elm.all) ? elm.all : elm.getElementsByTagName(tag),
                current,
                returnElements = [],
                match;
            for (var k = 0, kl = classes.length; k < kl; k += 1) {
                classesToCheck.push(new RegExp("(^|\\s)" + classes[k] + "(\\s|$)"));
            }
            for (var l = 0, ll = elements.length; l < ll; l += 1) {
                current = elements[l];
                match = false;
                for (var m = 0, ml = classesToCheck.length; m < ml; m += 1) {
                    match = classesToCheck[m].test(current.className);
                    if (!match) {
                        break;
                    }
                }
                if (match) {
                    returnElements.push(current);
                }
            }
            return returnElements;
        };
    }
    return getElementsByClassName(className, tag, elm);
};

!(function(d, w){

    if (!w.console) w.console = {};
    if (!w.console.log) w.console.log = function () { };
    if (!w.hasOwnProperty(LOADER_NS)) w[LOADER_NS] = {};

    var loadWidget = function(el, widget, config){

        var regex = /^data-(.+)/,
            paramsEmbed = {},
            match;
        [].forEach.call(el.attributes, function(attr){
            if (match = attr.name.match(regex)) {
                paramsEmbed[match[1]] = attr.value;
            }
        });
//        var width = (paramsEmbed['width'] || width) || 460,
//            height = (paramsEmbed['height'] || height) || 400,
//            url = (paramsEmbed['base_url'] || base_url) + '?' + encodeQueryData(paramsEmbed);
        el.innerHTML = '<iframe allowtransparency="true" frameBorder="0" scrolling="no" ' +
            'style="border: none; max-width: 100%; min-width: 180px;" ' +
            'width="'+(paramsEmbed['width'] || config['width'] || 460)+'" ' +
            'height="'+(paramsEmbed['height'] || config['height'] || 400)+'" ' +
            'src="'+ (paramsEmbed['base_url'] || config['base_url']) + '?' + encodeQueryData(paramsEmbed) +'"></iframe>';
    };

    var encodeQueryData = function(data) {
        /*
         http://stackoverflow.com/questions/111529/create-query-parameters-in-javascript
         */
        var ret = [];
        for (var k in data) {
            if (!data.hasOwnProperty(k)) continue;
            if ( k.endsWith('_set') ) {
                // this is a django-widgets convention
                data[k].split(',').forEach(function(val){
                    ret.push(encodeURIComponent(k) + "=" + encodeURIComponent(val));
                })
            } else {
                ret.push(encodeURIComponent(k) + "=" + encodeURIComponent(data[k]));
            }
        }
        return ret.join("&");
    };

    for(var widget in w[LOADER_NS]) {
        var els = locateWidgetElements(widget),
            nEls = els.length,
            foundEls = [],
            config = w[LOADER_NS][widget];

        for(var i = 0; i < nEls; i++) {
            var el = els[i];
            if(foundEls.indexOf(el) < 0) {
                foundEls.push(el);
                loadWidget(el, widget, config);
            }
        }
    }

})(document, window);
