const CourseDetailsApp = {
    methods: {
        async fillSectionsList(){
             const sectionsList = await axios.get(
                '/api/v1/courses/' + this.courseId +'/retrieve-assigned/',
                {
                    headers: {
                        Authorization: 'Token ' + window.localStorage.token
                    }
                }
            );
            this.sections = sectionsList.data.sections;
        }
    },
    data() {
        return {
            courseId: null,
            sections: []
        }
    },
    mounted() {
        this.courseId = window.location.pathname.split('/').slice(-2)[0];
        this.fillSectionsList().then();
    }
};

const app = Vue.createApp(CourseDetailsApp);
app.config.errorHandler = (error, vm, info) => {
    console.log(error);
};
app.mount('#app');

/*
TODO
Details can be retrieved from the already
existing endpoint on lessons. Additionally, I need to remember about showing by default the first
unfinished course and moving on to the next one on clicking "complete".
 */