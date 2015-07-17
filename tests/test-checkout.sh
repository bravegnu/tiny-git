#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
tig commit "Added goodbye world." > /dev/null
tig checkout ${sha1sum}

if grep "Goodbye World" file.txt; then
    echo "$0: FAILED"
else
    echo "$0: PASSED"
fi

popd > /dev/null

rm -fr ${tdir}
