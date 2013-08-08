/*!
  * domready (c) Dustin Diaz 2012 - License MIT
  * https://github.com/ded/domready
  * v0.2.12
  */
!function(e,t){typeof module!="undefined"?module.exports=t():typeof define=="function"&&typeof define.amd=="object"?define(t):this[e]=t()}("domready",function(e){function p(e){h=1;while(e=t.shift())e()}var t=[],n,r=!1,i=document,s=i.documentElement,o=s.doScroll,u="DOMContentLoaded",a="addEventListener",f="onreadystatechange",l="readyState",c=o?/^loaded|^c/:/^loaded|c/,h=c.test(i[l]);return i[a]&&i[a](u,n=function(){i.removeEventListener(u,n,r),p()},r),o&&i.attachEvent(f,n=function(){/^c/.test(i[l])&&(i.detachEvent(f,n),p())}),e=o?function(n){self!=top?h?n():t.push(n):function(){try{s.doScroll("left")}catch(t){return setTimeout(function(){e(n)},50)}n()}()}:function(e){h?e():t.push(e)}})
;

/*!
  * gator (c) Craig Campbell 2013 - License Apache 2.0
  * http://craig.is/riding/gators
  * v1.2.2
  */
(function(){function q(a,b,c){if("_root"==b)return c;if(a!==c){var d;k||(a.matches&&(k=a.matches),a.webkitMatchesSelector&&(k=a.webkitMatchesSelector),a.mozMatchesSelector&&(k=a.mozMatchesSelector),a.msMatchesSelector&&(k=a.msMatchesSelector),a.oMatchesSelector&&(k=a.oMatchesSelector),k||(k=e.matchesSelector));d=k;if(d.call(a,b))return a;if(a.parentNode)return m++,q(a.parentNode,b,c)}}function s(a,b,c,e){d[a.id]||(d[a.id]={});d[a.id][b]||(d[a.id][b]={});d[a.id][b][c]||(d[a.id][b][c]=[]);d[a.id][b][c].push(e)}function t(a,b,c,e){if(d[a.id])if(!b)for(var f in d[a.id])d[a.id].hasOwnProperty(f)&&(d[a.id][f]={});else if(!e&&!c)d[a.id][b]={};else if(!e)delete d[a.id][b][c];else if(d[a.id][b][c])for(f=0;f<d[a.id][b][c].length;f++)if(d[a.id][b][c][f]===e){d[a.id][b][c].splice(f,1);break}}function u(a,b,c){if(d[a][c]){var k=b.target||b.srcElement,f,g,h={},n=g=0;m=0;for(f in d[a][c])d[a][c].hasOwnProperty(f)&&(g=q(k,f,l[a].element))&&e.matchesEvent(c,l[a].element,g,"_root"==f,b)&&(m++,d[a][c][f].match=g,h[m]=d[a][c][f]);b.stopPropagation=function(){b.cancelBubble=!0};for(g=0;g<=m;g++)if(h[g])for(n=0;n<h[g].length;n++){if(!1===h[g][n].call(h[g].match,b)){e.cancel(b);return}if(b.cancelBubble)return}}}function r(a,b,c,k){function f(a){return function(b){u(g,b,a)}}if(this.element){a instanceof Array||(a=[a]);c||"function"!=typeof b||(c=b,b="_root");var g=this.id,h;for(h=0;h<a.length;h++)k?t(this,a[h],b,c):(d[g]&&d[g][a[h]]||e.addEvent(this,a[h],f(a[h])),s(this,a[h],b,c));return this}}function e(a,b){if(!(this instanceof e)){for(var c in l)if(l[c].element===a)return l[c];p++;l[p]=new e(a,p);return l[p]}this.element=a;this.id=b}var k,m=0,p=0,d={},l={};e.prototype.on=function(a,b,c){return r.call(this,a,b,c)};e.prototype.off=function(a,b,c){return r.call(this,a,b,c,!0)};e.matchesSelector=function(){};e.cancel=function(a){a.preventDefault();a.stopPropagation()};e.addEvent=function(a,b,c){a.element.addEventListener(b,c,"blur"==b||"focus"==b)};e.matchesEvent=function(){return!0};window.Gator=e})();
;

/**
 * Utility methods to work with DomNode models.
 */
var _w = (function(){
  'use strict';

  var doc = document,
    w = window,
    loc = w.location;

  function retina() {
    var win = window,
      mq = win.matchMedia ? win.matchMedia('only screen and (-moz-min-device-pixel-ratio: 1.3), only screen and (-o-min-device-pixel-ratio: 2.6/2), only screen and (-webkit-min-device-pixel-ratio: 1.3), only screen  and (min-device-pixel-ratio: 1.3), only screen and (min-resolution: 1.3dppx)') : {};

    return mq && mq.matches;
  }

  function init() {
    // Smooth scroll during page load
    if (loc.hash) {
      _scroll(loc.hash.substring(1));
    }

    // Smooth scroll when page links are clicked
    Gator(doc).on('click', 'a', function(e) {
      // Ignore in design mode
      if (typeof __wf_design != 'undefined' && __wf_design) {
        return;
      }

      // Find actual link, if one of its children is the event target
      var t = e.target;
      if (_tag(t) != 'a') {
        t = _up(t, 'a');
      }

      if (!t) {
        return;
      }

      var hash = t.hash ? t.hash.substring(1) : null;
      if (!hash) {
        return;
      }

      _scroll(hash, e);
    });
  }

  // Gets the normalized tag name
  function _tag(n) {
    return n ? n.nodeName.toLowerCase() : null;
  }

  // Walks up the DOM to find first parent with tag name
  function _up(n, tag) {
    var limit = 3;
    while (limit--) {
      n = n.parentNode;

      if (!n) {
        return null;
      }

      if (_tag(n) == tag) {
        return n;
      }
    }

    return null;
  }

  // Finds the first proper node child
  function _first(n) {
    var ch = n.childNodes;

    for (var i = 0, j = ch.length; i < j; i++) {
      var c = n.childNodes[i];
      if (c.nodeType === 1) {
        return c;
      }
    }

    return null;
  }

  // Gets the top position of a node in the document
  function _top(n) {
    var scrollY = window.pageYOffset;

    if (_tag(n) == 'html') {
      return -scrollY;
    }

    return _box(n).top + scrollY;
  }

  function _box(n) {
    return n.getBoundingClientRect();
  }

  function _ease(t) {
    return t<.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1;
  }

  function _pos(start, end, elapsed, duration) {
    if (elapsed > duration) {
      return end;
    }

    return start + (end - start) * _ease(elapsed / duration); 
  }

  function _scroll(hash, e) {
    var n = doc.getElementById(hash);
    if (!n) {
      return;
    }

    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    // Push new history state
    if (loc.hash !== hash) {
      w.history.pushState(null, null, '#' + hash);
    }

    // Adjust for fixed header
    var header = doc.getElementsByTagName('HEADER')[0] || _first(doc.body),
      styles = header ? w.getComputedStyle(header, null) : 0,
      fixed = styles && styles['position'] === 'fixed',
      offset = fixed ? parseInt(styles['height'].replace(/[^-\d\.]/g, ''), 10) : 0;

    // Smooth scroll
    if (e) {
      _buttah(n, offset);
    } else {
      w.setTimeout(function() {
        _buttah(n, offset);
      }, 300);
    }
  }

  function _buttah(n, offset, cb){
    var w = window,
      start = w.pageYOffset,
      end = _top(n) - offset,
      clock = Date.now(),
      animate = w.requestAnimationFrame || w.mozRequestAnimationFrame || w.webkitRequestAnimationFrame || function(fn) { window.setTimeout(fn, 15); },
      duration = 472.143 * Math.log(Math.abs(start - end) +125) - 2000,
      step = function() {
        var elapsed = Date.now() - clock;

        w.scroll(0, _pos(start, end, elapsed, duration));

        if (elapsed > duration) {
          if (cb) {
            cb(n);
          }
        } else {
          animate(step);
        }
      };

    step();
  }

  // API
  return {
    init: init,
    retina: retina
  };
})();

domready(function() {
  _w.init();
})