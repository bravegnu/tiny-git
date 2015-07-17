#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum_1=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
sha1sum_2=$(tig commit "Added goodbye world.")
tig log > ${tdir}/log.txt

cat > ${tdir}/log2.txt <<EOF
${sha1sum_2:0:6} Added goodbye world.
${sha1sum_1:0:6} Initial content.
EOF

if diff ${tdir}/log.txt ${tdir}/log2.txt; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
