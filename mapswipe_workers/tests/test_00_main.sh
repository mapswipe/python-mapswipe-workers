python test_01_create_projects.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_02_mapping.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_03_firebase_to_postgres.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_04_generate_stats.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_05_clean_up.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi