test:
	nosetests -s

clean:
	find -name "*.pyc" | xargs rm

.PHONY = test
