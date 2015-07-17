#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
tig commit "Initial content." > /dev/null
echo "Goodbye World" >> file.txt
if tig diff | grep "+Goodbye World" > /dev/null; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
rm -f ${sha1sum}