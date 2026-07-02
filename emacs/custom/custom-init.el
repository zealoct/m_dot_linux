(require 'setup-ui)
(require 'setup-editing)
(require 'setup-languages)

(cond
 ((eq system-type 'darwin)
  (require 'setup-vertico)
  (setq mac-option-key-is-meta nil)
  (setq mac-command-key-is-meta t)
  (setq mac-command-modifier 'meta)
  (setq mac-option-modifier nil))
 ((eq system-type 'gnu/linux)
  (require 'setup-vertico)))

(provide 'custom-init)
