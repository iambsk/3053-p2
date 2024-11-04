run:
	@if [ -z "$(x)" ]; then \
		echo "Usage: make run x=<number_of_nodes>"; \
	else \
		python3 main.py $(x); \
	fi

genrun:
	@if [ -z "$(x)" ]; then \
		echo "Usage: make run x=<number_of_nodes>"; \
	else \
		python3 nodeGen.py $(x); \
		python3 main.py $(x); \
	fi

# Clean target to remove all node{x}.txt files
clean:
	rm -f node*.txt
