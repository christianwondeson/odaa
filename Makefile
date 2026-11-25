PY=python3
# Narration language: make radio NARRATION_LANG=oro   (default am)
export NARRATION_LANG ?= am
.PHONY: env-check validate smoke narration radio keyframes shots music film clean-cache
env-check:  ; $(PY) -m pipeline.check_env
validate:   ; $(PY) -m pipeline.validate
smoke:      ; $(PY) -m pipeline.smoke_test
narration:  validate ; $(PY) -m pipeline.narration
radio:      narration ; $(PY) -m pipeline.assemble radio
keyframes:  validate ; $(PY) -m pipeline.keyframes
shots:      keyframes narration ; $(PY) -m pipeline.shots
music:      validate ; $(PY) -m pipeline.music
film:       validate narration keyframes shots music ; $(PY) -m pipeline.assemble film
clean-cache:; rm -f outputs/.cache.json
