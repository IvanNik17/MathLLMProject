import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import "./driver.css";

export function startTutorial(
  setTutorialActive: (active: boolean) => void
) {
  const driverObj = driver({
    showProgress: true,
    disableActiveInteraction: true,

    onDestroyed: () => {
      setTutorialActive(false);
    },

    steps: [
      {
        element: "#current-problem",
        popover: {
          title: "Current problem",
          description: "This is the problem you'll be working on. Take a moment to read through it before getting started."
        }
      },
        {
          element: "#answer-write",
            popover: {
              title: "Write Your Answer",
                description: "Enter your solution here once you've worked it out!"
            }
        },
        {
          element: "#add-solution",
            popover: {
              title: "Multiple Solutions",
                description: "Some problems have more than one solution. Use this button to add additional answer fields so you can enter them all."
            }
        },
        {
            element: "#shortcuts",
            popover: {
                title: "Shortcuts",
                description:  "Need to enter mathematical symbols? These shortcuts make it easier to write your answers."
            }
        },
        {
            element: "#check-answer",
            popover: {
                title: "Check Your Answer!",
                description: "Once you've entered your solution, click here to check whether your answer is correct."
            }
        },
        {
            element: "#problem-list",
            popover: {
                title: "Problem List",
                description: "Ready for another challenge? Choose a different problem from the list and keep practising!"
            }
        }
    ]
  });

  setTutorialActive(true);
  driverObj.drive();
}