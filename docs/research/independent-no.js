(function () {
  'use strict';

  var explorer = document.querySelector('[data-explorer]');
  if (!explorer) return;

  var controls = Array.from(explorer.querySelectorAll('[data-surface]'));
  var count = document.getElementById('judge-count');
  var names = {
    rules: 'rewrite the passing rule',
    evidence: 'replace the admitted evidence',
    scope: 'substitute a different question',
    release: 'bypass the checked release route'
  };

  function update() {
    var enabled = controls.filter(function (input) { return input.checked; });
    var bypasses = enabled.filter(function (input) { return input.dataset.surface !== 'receipt'; });
    var lostReceipt = enabled.some(function (input) { return input.dataset.surface === 'receipt'; });
    var n = Number(count.value);

    controls.forEach(function (input) {
      input.closest('label').querySelector('.control-state').textContent = input.checked ? 'Editable' : 'Protected';
    });

    document.getElementById('judge-verdict').textContent =
      n + (n === 1 ? ' judge rejects' : ' judges reject') + ' the original claim.';
    var outcome = document.getElementById('outcome-box');
    outcome.dataset.status = bypasses.length ? 'bypass' : (lostReceipt ? 'history-lost' : 'protected');
    document.getElementById('release-outcome').textContent =
      bypasses.length ? 'False support has a route.' : 'Rejection remains binding.';
    document.getElementById('release-explanation').textContent = bypasses.length
      ? 'In this toy, the generator may ' + bypasses.map(function (input) { return names[input.dataset.surface]; }).join('; ') + '. More correct judges do not remove those powers.'
      : 'No stipulated route can turn this rejected evaluation into a supported claim.';
    document.getElementById('receipt-outcome').textContent = lostReceipt ? 'Can be erased' : 'Retained';
    document.getElementById('survival-outcome').textContent =
      bypasses.length || lostReceipt ? 'Does not survive' : 'Survives in this model';
    document.getElementById('comparison-note').textContent =
      'Matched conventional controls: the same outcome. Both descriptions use the same permissions.';
  }

  controls.forEach(function (input) { input.addEventListener('change', update); });
  count.addEventListener('change', update);
  document.getElementById('reset-explorer').addEventListener('click', function () {
    controls.forEach(function (input) { input.checked = false; });
    count.value = '1';
    update();
  });

  update();
  explorer.hidden = false;
}());
