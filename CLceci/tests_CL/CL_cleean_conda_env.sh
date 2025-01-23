#!/bin/bash

envParam=`printenv | grep ^CONDA`

echo "$envParam"

# Remove all environment parameter starting with CONDA
for i in $(echo $envParam| tr ";" "\n")
do
    if [[ "$i" =~ ^CONDA.* ]]; then
	echo ">>>>> $i"

	array=($(echo $i | tr "=" " "))	
	mycmd=(unset "${array[0]}")
	"${mycmd[@]}"
    fi
done

# Remove condabin from PATH

initPath="$PATH"

for i in $(echo $initPath| tr ":" "\n")
do
    if [[ "$i" =~ condabin.* ]]; then
	echo ">>>>> $i"
	strToRemove="$i:"
	echo "To remove : $strToRemove"
	newPath="${initPath#${strToRemove}}"
	export PATH=$newPath
	echo "PATH : $PATH"
    fi
done
